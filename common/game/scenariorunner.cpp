#include "scenariorunner.h"

#include <Tempest/Log>
#include <Tempest/SystemApi>
#include <Tempest/TextCodec>

#include <cctype>
#include <charconv>
#include <cstdio>
#include <filesystem>
#include <fstream>

#include "game/fightlog.h"
#include "utils/string_frm.h"
#include "commandline.h"
#include "gothic.h"

using namespace Tempest;

static std::vector<std::string_view> split(std::string_view s) {
  std::vector<std::string_view> ret;
  for(size_t i=0; i<s.size();) {
    while(i<s.size() && (s[i]==' ' || s[i]=='\t'))
      ++i;
    size_t e = i;
    while(e<s.size() && s[e]!=' ' && s[e]!='\t')
      ++e;
    if(e>i)
      ret.push_back(s.substr(i,e-i));
    i = e;
    }
  return ret;
  }

static bool compareNoCase(std::string_view a, std::string_view b) {
  if(a.size()!=b.size())
    return false;
  for(size_t i=0; i<a.size(); ++i)
    if(std::tolower(a[i])!=std::tolower(b[i]))
      return false;
  return true;
  }

static std::string jsonText(std::string_view v) {
  std::string s = "\"";
  for(char c:v) {
    const uint8_t b = uint8_t(c);
    if(c=='"' || c=='\\') {
      s.push_back('\\');
      s.push_back(c);
      }
    else if(b<0x20 || b>=0x80) {
      char buf[8] = {};
      std::snprintf(buf,sizeof(buf),"\\u%04x",unsigned(b));
      s += buf;
      }
    else {
      s.push_back(c);
      }
    }
  s.push_back('"');
  return s;
  }

ScenarioRunner::ScenarioRunner() {
  auto& cmd = CommandLine::inst();
  if(cmd.scenarioPath().empty())
    return;
  if(!cmd.isDevMode()) {
    Log::e("scenario: -scenario requires -devmode");
    state = S_Done;
    return;
    }
  marvin.print.bind(this,&ScenarioRunner::onPrint);
  exitOnEnd = cmd.isScenarioExit();
  load(cmd.scenarioPath());
  }

void ScenarioRunner::load(std::u16string_view file) {
  std::ifstream in{std::filesystem::path(file)};
  if(!in) {
    fail(-1,string_frm("unable to read \"",TextCodec::toUtf8(file),"\""));
    return;
    }

  std::string s;
  for(int32_t num=1; std::getline(in,s); ++num) {
    if(num==1 && s.rfind("\xEF\xBB\xBF",0)==0)
      s.erase(0,3);
    while(!s.empty() && std::isspace(uint8_t(s.back())))
      s.pop_back();
    while(!s.empty() && std::isspace(uint8_t(s.front())))
      s.erase(0,1);
    if(s.empty() || s[0]=='#')
      continue;

    auto args = split(s);
    if(compareNoCase(args[0],"expect"))
      continue; // checked by the report, not by the engine

    Line l;
    l.num  = num;
    l.text = s;
    if(compareNoCase(args[0],"wait")) {
      float sec = -1;
      if(args.size()==2)
        std::from_chars(args[1].data(), args[1].data()+args[1].size(), sec);
      if(sec<0) {
        fail(num,"wait expects a time in seconds");
        return;
        }
      l.kind   = K_Wait;
      l.waitMs = uint64_t(sec*1000.f);
      }
    else if(compareNoCase(args[0],"quit") && args.size()==1) {
      l.kind = K_Quit;
      }
    lines.push_back(std::move(l));
    }

  writeStatus("running",-1,"");
  Log::i("scenario: ",int(lines.size())," commands from \"",TextCodec::toUtf8(file),"\"");
  }

void ScenarioRunner::onWorldLoaded() {
  // NOTE: called again once a save is written - scenario starts only once
  if(state!=S_Idle || CommandLine::inst().scenarioPath().empty())
    return;
  state = S_Running;
  FightLog::setEnabled(true);
  FightLog::marker("scenario_start",-1,TextCodec::toUtf8(CommandLine::inst().scenarioPath()));
  Log::i("scenario: start");
  }

void ScenarioRunner::tick() {
  if(state!=S_Running)
    return;
  auto world = Gothic::inst().world();
  if(world==nullptr || Gothic::inst().checkLoading()!=Gothic::LoadState::Idle)
    return;

  if(!saveFile.empty()) {
    // saving runs on the loader thread: it is done, once the loading state is idle again
    std::error_code ec;
    if(!std::filesystem::exists(saveFile,ec)) {
      fail(saveLine,string_frm("save file \"",saveFile,"\" was not written"));
      return;
      }
    FightLog::marker("save",saveLine,"",saveFile);
    saveFile.clear();
    }

  const uint64_t now = world->tickCount();
  if(now<waitUntil)
    return;

  while(state==S_Running && pc<lines.size()) {
    exec(lines[pc++],now);
    if(waitUntil>now || !saveFile.empty())
      return;
    if(Gothic::inst().world()!=world || Gothic::inst().checkLoading()!=Gothic::LoadState::Idle)
      return;
    }
  if(state==S_Running)
    finish(false);
  }

void ScenarioRunner::exec(const Line& l, uint64_t now) {
  FightLog::marker("line",l.num,l.text);
  switch(l.kind) {
    case K_Wait:
      waitUntil = now + l.waitMs;
      return;
    case K_Quit:
      finish(true);
      return;
    case K_Console:
      break;
    }

  const auto  args = split(l.text);
  std::string save;
  if(args.size()==3 && compareNoCase(args[0],"save") && compareNoCase(args[1],"game")) {
    // an old file would hide a failed save
    save = std::string(string_frm("save_slot_",args[2],".sav"));
    std::error_code ec;
    std::filesystem::remove(save,ec);
    }

  lastPrint.clear();
  if(!marvin.exec(l.text)) {
    if(lastPrint.empty())
      fail(l.num,string_frm("command failed: ",l.text)); else
      fail(l.num,string_frm("command failed: ",l.text,": ",lastPrint));
    return;
    }

  if(!save.empty()) {
    saveFile = save;
    saveLine = l.num;
    }
  if(args.size()==2 && compareNoCase(args[0],"screenshot"))
    FightLog::marker("screenshot",l.num,"",TextCodec::toUtf8(CommandLine::inst().resultsFile(args[1])));
  }

void ScenarioRunner::finish(bool quit) {
  state = S_Done;
  Log::i("scenario: done");
  FightLog::marker("scenario_end");
  writeStatus("ok",-1,"");
  if(quit || exitOnEnd)
    SystemApi::exit();
  }

void ScenarioRunner::fail(int32_t line, std::string_view msg) {
  state = S_Done;
  Log::e("scenario: line ",int(line),": ",msg);
  FightLog::marker("scenario_end",line,msg);
  writeStatus("error",line,msg);
  if(exitOnEnd)
    SystemApi::exit();
  }

void ScenarioRunner::writeStatus(std::string_view result, int32_t line, std::string_view msg) {
  auto          file = CommandLine::inst().resultsFile("scenario.json");
  auto          w    = Gothic::inst().world();
  std::ofstream out(std::filesystem::path(file), std::ios::binary | std::ios::trunc);
  out << "{\"result\":" << jsonText(result)
      << ",\"line\":"   << (line>=0 ? std::to_string(line) : std::string("null"))
      << ",\"message\":"<< jsonText(msg)
      << ",\"t\":"      << (w!=nullptr ? w->tickCount() : 0)
      << "}\n";
  }

void ScenarioRunner::onPrint(std::string_view msg) {
  Log::i("scenario: ",msg);
  lastPrint = msg;
  }
