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
#include "world/objects/npc.h"
#include "world/world.h"
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
  FightLog::onEvent.bind(this,&ScenarioRunner::onFightEvent);
  exitOnEnd = cmd.isScenarioExit();
  load(cmd.scenarioPath());
  }

ScenarioRunner::~ScenarioRunner() {
  FightLog::onEvent.ubind(this,&ScenarioRunner::onFightEvent);
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
    if(compareNoCase(args[0],"wait") && args.size()>2) {
      if(!parseEventWait(l,args)) {
        fail(num,"expected: wait <who> series|series-hit <n>|combo <n>|down|unconscious|dead timeout <seconds>");
        return;
        }
      }
    else if(compareNoCase(args[0],"wait")) {
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

bool ScenarioRunner::parseEventWait(Line& l, const std::vector<std::string_view>& args) {
  // wait <who> <event> [n] timeout <seconds>
  static const struct {
    std::string_view name;
    EventKind        kind;
    bool             count;
    } events[] = {
    {"series",      E_Series,      false},
    {"series-hit",  E_SeriesHit,   true },
    {"combo",       E_Combo,       true },
    {"down",        E_Down,        false},
    {"unconscious", E_Unconscious, false},
    {"dead",        E_Dead,        false},
    };

  for(auto& ev:events) {
    if(!compareNoCase(args[2],ev.name))
      continue;
    const size_t at = ev.count ? 4 : 3;
    if(args.size()!=at+2 || !compareNoCase(args[at],"timeout"))
      return false;
    if(ev.count) {
      auto err = std::from_chars(args[3].data(), args[3].data()+args[3].size(), l.n).ec;
      if(err!=std::errc() || l.n<1)
        return false;
      }
    float sec = -1;
    std::from_chars(args[at+1].data(), args[at+1].data()+args[at+1].size(), sec);
    if(sec<=0)
      return false;
    l.kind   = K_WaitEvent;
    l.event  = ev.kind;
    l.who    = std::string(args[1]);
    l.waitMs = uint64_t(sec*1000.f);
    return true;
    }
  return false;
  }

void ScenarioRunner::onWorldLoaded() {
  // NOTE: called again once a save is written - scenario starts only once
  if(state!=S_Idle || CommandLine::inst().scenarioPath().empty())
    return;
  if(Gothic::inst().world()==nullptr) {
    // called after a failed load as well
    fail(-1,"the world did not load, see log.txt");
    return;
    }
  state = S_Running;
  FightLog::setEnabled(true);
  FightLog::marker("scenario_start",-1,TextCodec::toUtf8(CommandLine::inst().scenarioPath()));
  Log::i("scenario: start");
  // first commands run before the world moves: e.g. 'cheat god' before a pending hit of a loaded save
  tick();
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
  if(evWait.line!=nullptr) {
    if(!evWait.done) {
      if(now>=evWait.deadline)
        fail(evWait.line->num,string_frm("time limit reached: ",evWait.line->text));
      return;
      }
    evWait = EventWait();
    }
  if(now<waitUntil)
    return;

  while(state==S_Running && pc<lines.size()) {
    exec(lines[pc++],now);
    if(waitUntil>now || !saveFile.empty() || evWait.line!=nullptr)
      return;
    if(Gothic::inst().world()!=world || Gothic::inst().checkLoading()!=Gothic::LoadState::Idle)
      return;
    }
  if(state==S_Running)
    finish();
  }

void ScenarioRunner::exec(const Line& l, uint64_t now) {
  FightLog::marker("line",l.num,l.text);
  switch(l.kind) {
    case K_Wait:
      waitUntil = now + l.waitMs;
      return;
    case K_WaitEvent: {
      // events count from now on, see onFightEvent
      EventWait w;
      w.line     = &l;
      w.deadline = now + l.waitMs;
      if(compareNoCase(l.who,"hero")) {
        w.hero = true;
        } else {
        w.instance = Gothic::inst().world()->script().findSymbolIndex(l.who);
        if(w.instance==size_t(-1)) {
          fail(l.num,string_frm("unknown instance \"",l.who,"\""));
          return;
          }
        }
      evWait = w;
      return;
      }
    case K_Quit:
      // without -scenario-exit (manual mode) the game stays open
      finish();
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

void ScenarioRunner::finish() {
  state = S_Done;
  Log::i("scenario: done");
  FightLog::marker("scenario_end");
  writeStatus("ok",-1,"");
  if(exitOnEnd)
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

void ScenarioRunner::onFightEvent(const FightLog::Event& e) {
  if(evWait.line==nullptr || evWait.done || e.npc==nullptr)
    return;
  if(evWait.hero ? !e.npc->isPlayer() : e.npc->instanceSymbol()!=evWait.instance)
    return;

  const Line& l     = *evWait.line;
  bool        match = false;
  if(e.type=="attack") {
    switch(l.event) {
      case E_Series:    match = (e.seriesPos==1 && e.seriesLen>1); break;
      case E_SeriesHit: match = (e.seriesPos==l.n);                break;
      case E_Combo:     match = (e.combo==l.n);                    break;
      default:
        break;
      }
    } else {
    switch(l.event) {
      case E_Down:        match = (e.state=="lie" || e.state=="unconscious" || e.state=="dead"); break;
      case E_Unconscious: match = (e.state=="unconscious"); break;
      case E_Dead:        match = (e.state=="dead");        break;
      default:
        break;
      }
    }

  if(match) {
    evWait.done = true;
    FightLog::marker("wait_done",l.num,l.text);
    }
  }

void ScenarioRunner::onPrint(std::string_view msg) {
  Log::i("scenario: ",msg);
  lastPrint = msg;
  }
