#include "marvin.h"

#include <Tempest/SystemApi>
#include <Tempest/TextCodec>

#include <algorithm>
#include <charconv>
#include <cmath>
#include <cstdint>
#include <cctype>
#include <filesystem>

#include "game/fightlog.h"
#include "physics/dynamicworld.h"
#include "utils/string_frm.h"
#include "world/objects/npc.h"
#include "world/objects/item.h"
#include "world/triggers/abstracttrigger.h"
#include "camera.h"
#include "commandline.h"
#include "gothic.h"

static bool startsWith(std::string_view str, std::string_view needle) {
  if(needle.size()>str.size())
    return false;
  for(size_t i=0; i<needle.size(); ++i) {
    int n = std::tolower(needle[i]);
    int s = std::tolower(str   [i]);
    if(n!=s)
      return false;
    }
  return true;
  }

static bool compareNoCase(std::string_view sa, std::string_view sb) {
  if(sa.size()!=sb.size())
    return false;
  for(size_t i=0; i<sa.size(); ++i) {
    int a = std::tolower(sa[i]);
    int b = std::tolower(sb[i]);
    if(a!=b)
      return false;
    }
  return true;
  }

// a bit in front of the player, so that a big npc doesn't get stuck in him; closer, if a wall is in the way
static Tempest::Vec3 insertPosition(World& world, Npc& player) {
  const float distance = 200.f;
  const float rot      = player.rotationRad();
  const auto  dir      = Tempest::Vec3(std::cos(rot), 0, std::sin(rot));
  const auto  from     = player.collosionCenter();
  const auto  hit      = world.physic()->ray(from, from+dir*distance);
  float       len      = distance;
  if(hit.hasCol)
    len = std::max(0.f, distance*hit.hitFraction - 50.f);
  return player.position() + dir*len;
  }

template<class T>
static bool fromString(std::string_view str, T& t) {
  auto err = std::from_chars(str.data(), str.data()+str.size(),t).ec;
  if(err!=std::errc())
    return false;
  return true;
  }

static bool fromString(std::string_view str, float& t) {
  t = std::stof(std::string(str));
  return true;
  }

Marvin::Marvin() {
  /* Legend:
   %c - instance variable from script
   %v - variable from script
   %s - any string
   %d - integer
   %f - floating point number
   %* - rest of the input, may be empty
   */
  // http://forenarchiv.worldofplayers.de/thread.php?id=85859&post=45890#45890
  cmd = std::vector<Cmd>{
    // gdb-like commands
    {"p %v",                       C_PrintVar},
    // similar to "Marvin Helper" https://steamcommunity.com/sharedfiles/filedetails/?id=2847617433
    {"set var %v %s",              C_SetVar},
    {"call %v %*",                 C_Call},

    // animation
    {"play ani %c %s",             C_PlayAniNpc},
    {"play ani %s",                C_PlayAni},
    {"ani info %c %s",             C_AniInfo},
    {"play faceani %s",            C_Invalid},
    {"remove overlaymds %s",       C_Invalid},
    {"toggle aniinfo",             C_Invalid},
    {"zoverlaymds apply",          C_Invalid},
    {"zoverlaymds remove",         C_Invalid},
    {"zstartani %s %s",            C_Invalid},
    {"ztoggle modelskeleton",      C_Invalid},
    {"ztoggle rootsmoothnode",     C_Invalid},
    {"ztoggle vobmorph",           C_Invalid},

    // rendering
    {"set clipfactor %d",          C_Invalid},
    {"toggle frame",               C_ToggleFrame},
    {"zfogzone",                   C_Invalid},
    {"zhighqualityrender",         C_Invalid},
    {"zmark",                      C_Invalid},
    {"zprogmeshlod",               C_Invalid},
    {"zrmode flat",                C_Invalid},
    {"zrmode mat",                 C_Invalid},
    {"zrmode wire",                C_Invalid},
    {"zrmode wmat",                C_Invalid},
    {"zset levelclipscaler %f",    C_Invalid},
    {"zset nearclipz %f",          C_Invalid},
    {"zset vobfarclipscaler %f",   C_Invalid},
    {"ztoggle ambientvobs",        C_Invalid},
    {"ztoggle flushambientcol",    C_Invalid},
    {"ztoggle lightstat",          C_Invalid},
    {"ztoggle markpmeshmaterials", C_Invalid},
    {"ztoggle matmorph",           C_Invalid},
    {"ztoggle renderorder",        C_Invalid},
    {"ztoggle renderportals",      C_Invalid},
    {"ztoggle rendervob",          C_Invalid},
    {"ztoggle showportals",        C_Invalid},
    {"ztoggle showtraceray",       C_ToggleShowRay},
    {"ztoggle tnl",                C_Invalid},
    {"ztoggle vobbox",             C_ToggleVobBox},
    {"zvideores %d %d %d",         C_Invalid},

    // game
    {"LC1",                        C_Invalid},
    {"LC2",                        C_Invalid},
    {"load game",                  C_Invalid},
    {"save game %d",               C_SaveGame},
    {"save zen",                   C_Invalid},
    {"set time %d %d",             C_SetTime},
    {"spawnmass %d",               C_Invalid},
    {"spawnmass giga %d",          C_Invalid},
    {"toggle desktop",             C_ToggleDesktop},
    {"toggle freepoints",          C_Invalid},
    {"toggle screen",              C_Invalid},
    {"toggle time",                C_ToggleTime},
    {"toggle wayboxes",            C_Invalid},
    {"toggle waynet",              C_Invalid},
    {"version",                    C_Invalid},
    {"zstartrain",                 C_Invalid},
    {"zstartsnow",                 C_Invalid},
    {"ztimer multiplyer %f",       C_TimeMultiplyer},
    {"ztimer realtime",            C_TimeRealtime},
    {"ztoggle helpervisuals",      C_Invalid},
    {"ztoggle showzones",          C_Invalid},
    {"ztrigger %s",                C_ZTrigger},
    {"zuntrigger %s",              C_ZUntrigger},

    {"cheat full",                 C_CheatFull},
    {"cheat god",                  C_CheatGod},
    {"kill",                       C_Kill},

    {"aigoto %s",                  C_AiGoTo},
    {"goto waypoint %s",           C_GoToWayPoint},
    {"goto pos %f %f %f",          C_GoToPos},
    {"goto vob %c %d",             C_GoToVob},
    {"goto camera",                C_GoToCamera},

    {"camera autoswitch",          C_CamAutoswitch},
    {"camera mode",                C_CamMode},
    {"toggle camdebug",            C_ToggleCamDebug},
    {"toggle camera",              C_ToggleCamera},
    {"toggle inertiatarget",       C_ToggleInertia},
    {"ztoggle timedemo",           C_ZToggleTimeDemo},
    {"insert %c",                  C_Insert},
    {"give %c %*",                 C_Give},
    {"equip %c",                   C_Equip},
    {"screenshot %s",              C_Screenshot},
    {"toggle fightlog",            C_ToggleFightLog},
    {"info told %c",               C_InfoTold},
    {"immortal %c",                C_Immortal},
    {"remove npc %c %d",           C_RemoveNpc},
    {"quit",                       C_Quit},

    {"toggle gi",                  C_ToggleGI},
    {"toggle vsm",                 C_ToggleVsm},
    {"toggle rtsm",                C_ToggleRtsm},
    {"toggle pathtrace",           C_TogglePathtrace},
    };
  }

Marvin::CmdVal Marvin::isMatch(std::string_view inp, const Cmd& cmd) const {
  std::string_view ref  = cmd.cmd;
  CmdVal           ret  = C_Invalid;
  int              argc = 0;

  while(!ref.empty()) {
    if(ref=="%*") {
      if(argc<4)
        ret.argv[argc] = inp;
      break;
      }

    size_t wr = ref.find(' ');
    if(wr==std::string_view::npos)
      wr = ref.size();
    size_t wi = inp.find(' ');
    if(wi==std::string_view::npos)
      wi = inp.size();

    auto wref = ref.substr(0,wr);
    auto winp = inp.substr(0,wi);

    bool fullword = true;
    if(wref=="%c")
      wref = completeInstanceName(winp,fullword);
    else if(wref=="%v")
      wref = completeInstanceName(winp,fullword);
    else if(wref=="%s")
      wref = winp;
    else if(wref=="%f" || wref=="%d")
      wref = winp;

    if(!compareNoCase(wref,winp)) {
      if(!startsWith(wref,winp))
        return C_Invalid;
      ret.cmd      = cmd;
      ret.cmd.type = C_Incomplete;
      ret.complete = wref.substr(winp.size());
      ret.fullword = fullword;
      return ret;
      }

    if(ref[0]=='%' && argc<4) {
      ret.argv[argc] = wref;
      ++argc;
      }

    if(ref.size()==wr) {
      if(inp.size()!=winp.size())
        return C_Extra;
      break;
      }

    if(inp.size()==winp.size() && ref.substr(wr+1)=="%*")
      break;

    if(inp.size()==wr)
      return C_Incomplete;

    ref = ref.substr(wr+1);
    inp = inp.substr(std::min(wi+1,inp.size()));
    while(inp.size()>0 && inp[0]==' ')
      inp = inp.substr(1);
    }

  ret.cmd = cmd;
  return ret;
  }

Marvin::CmdVal Marvin::recognize(std::string_view inp) {
  while(inp.size()>0 && inp.back()==' ')
    inp = inp.substr(0,inp.size()-1);
  while(inp.size()>0 && inp[0]==' ')
    inp = inp.substr(1);

  if(inp.size()==0)
    return C_None;

  CmdVal suggestion = C_Invalid;

  for(auto& i:cmd) {
    auto m = isMatch(inp,i);
    if(m.cmd.type==C_Invalid)
      continue;
    if(m.cmd.type!=C_Incomplete)
      return m;
    if(suggestion.cmd.type==C_Incomplete) {
      if(suggestion.cmd.cmd!=m.cmd.cmd && suggestion.complete!=m.complete)
        return C_Incomplete; // multiple distinct commands do match - no suggestion
      suggestion = m;
      continue;
      }
    suggestion = m;
    }

  return suggestion;
  }

bool Marvin::autoComplete(std::string& v) {
  auto ret = recognize(v);
  if(ret.cmd.type==C_Incomplete && !ret.complete.empty()) {
    for(auto& i:ret.complete)
      v.push_back(i);
    if(ret.fullword)
      v.push_back(' ');
    return true;
    }
  return false;
  }

bool Marvin::exec(std::string_view v) {
  auto ret = recognize(v);
  switch(ret.cmd.type) {
    case C_None:
      return true;
    case C_Incomplete:
    case C_Invalid:
    case C_Extra:
      return false;
    case C_CheatFull:{
      if(auto pl = Gothic::inst().player()) {
        pl->changeAttribute(ATR_HITPOINTS,pl->attribute(ATR_HITPOINTSMAX),false);
        }
      return true;
      }
    case C_CheatGod: {
      auto& fnt = Resources::font(1.0);
      if(Gothic::inst().isGodMode()) {
        Gothic::inst().setGodMode(false);
        Gothic::inst().onPrintScreen("Godmode off",2,4,1,fnt);
        } else {
        Gothic::inst().setGodMode(true);
        Gothic::inst().onPrintScreen("Godmode on",2,4,1,fnt);
        }
      return true;
      }
    case C_Kill: {
      Npc* player = Gothic::inst().player();
      if(player==nullptr || player->target()==nullptr)
        return false;
      auto target = player->target();
      target->changeAttribute(ATR_HITPOINTS,-target->attribute(ATR_HITPOINTSMAX),false);
      return true;
      }
    case C_AiGoTo: {
      World* world  = Gothic::inst().world();
      Npc*   player = Gothic::inst().player();
      if(world==nullptr || player==nullptr || !player->setInteraction(nullptr))
        return false;
      auto wpoint = world->findPoint(ret.argv[0]);
      if(wpoint==nullptr)
        return false;
      player->aiPush(AiQueue::aiGoToPoint(*wpoint));
      return true;
      }
    case C_GoToPos: {
      Npc* player = Gothic::inst().player();
      if(player==nullptr || !player->setInteraction(nullptr))
        return false;
      int c[3] = {};
      for(int i=0; i<3; ++i) {
        if(!fromString(ret.argv[i], c[i]))
          return false;
        }
      player->setPosition(float(c[0]),float(c[1]),float(c[2]));
      player->updateTransform();
      Gothic::inst().camera()->reset(player);
      return true;
      }
    case C_GoToWayPoint: {
      World* world  = Gothic::inst().world();
      Npc*   player = Gothic::inst().player();
      if(world==nullptr || player==nullptr || !player->setInteraction(nullptr))
        return false;
      auto wpoint = world->findPoint(ret.argv[0]);
      if(wpoint==nullptr)
        return false;
      player->setPosition(wpoint->position());
      player->updateTransform();
      Gothic::inst().camera()->reset(player);
      return true;
      }
    case C_GoToVob: {
      World* world  = Gothic::inst().world();
      Npc*   player = Gothic::inst().player();
      auto   c      = Gothic::inst().camera();
      if(world==nullptr || c==nullptr || player==nullptr)
        return false;
      size_t n = 1;
      if(!ret.argv[1].empty() && !fromString(ret.argv[1], n)) {
        return false;
        }
      return goToVob(*world,*player,*c,ret.argv[0],--n);
      }
    case C_GoToCamera: {
      auto c      = Gothic::inst().camera();
      Npc* player = Gothic::inst().player();
      if(c==nullptr || player==nullptr)
        return false;
      auto pos = c->destTarget();
      player->setPosition(pos.x,pos.y,pos.z);
      player->updateTransform();
      c->reset();
      return true;
      }
    case C_ToggleFrame:{
      Gothic::inst().setFRate(!Gothic::inst().doFrate());
      return true;
      }
    case C_ToggleShowRay:{
      Gothic::inst().setVobRays(!Gothic::inst().doVobRays());
      return true;
      }
    case C_ToggleVobBox:{
      Gothic::inst().setVobBox(!Gothic::inst().doVobBox());
      return true;
      }
    case C_ToggleTime:{
      Gothic::inst().setClock(!Gothic::inst().doClock());
      return true;
      }
    case C_TimeMultiplyer: {
      if(auto g = Gothic::inst().gameSession()) {
        float mul = 1;
        if(!fromString(ret.argv[0], mul))
          return false;
        mul = std::max(mul, 0.f);
        g->setTimeMultiplyer(mul);
        return true;
        }
      return false;
      }
    case C_TimeRealtime:{
      if(auto g = Gothic::inst().gameSession()) {
        g->setTimeMultiplyer(1);
        return true;
        }
      return false;
      }
    case C_CamAutoswitch:
      return true;
    case C_CamMode:
      return true;
    case C_ToggleCamDebug:
      if(auto c = Gothic::inst().camera())
        c->toggleDebug();
      return true;
    case C_ToggleCamera: {
      if(auto c = Gothic::inst().camera())
        c->setToggleEnable(!c->isToggleEnabled());
      return true;
      }
    case C_ToggleInertia: {
      if(auto c = Gothic::inst().camera())
        c->setInertiaTargetEnable(!c->isInertiaTargetEnabled());
      return true;
      }
    case C_ZToggleTimeDemo: {
      World* world = Gothic::inst().world();
      if(world==nullptr)
        return false;
      const TriggerEvent evt("TIMEDEMO","",world->tickCount(),TriggerEvent::T_Trigger);
      world->triggerEvent(evt);
      return true;
      }
    case C_ToggleDesktop: {
      Gothic::inst().toggleDesktop();
      return true;
      }
    case C_ZTrigger: {
      World* world = Gothic::inst().world();
      if(world==nullptr)
        return false;
      const TriggerEvent evt(std::string(ret.argv[0]),"",world->tickCount(),TriggerEvent::T_Trigger);
      world->triggerEvent(evt);
      return true;
      }
    case C_ZUntrigger: {
      World* world = Gothic::inst().world();
      if(world==nullptr)
        return false;
      const TriggerEvent evt(std::string(ret.argv[0]),"",world->tickCount(),TriggerEvent::T_Untrigger);
      world->triggerEvent(evt);
      return true;
      }
    case C_Insert: {
      World* world  = Gothic::inst().world();
      Npc*   player = Gothic::inst().player();
      if(world==nullptr || player==nullptr)
        return false;
      return addItemOrNpcBySymbolName(world, ret.argv[0], insertPosition(*world, *player));
      }
    case C_Give: {
      World* world  = Gothic::inst().world();
      Npc*   player = Gothic::inst().player();
      if(world==nullptr || player==nullptr)
        return false;
      size_t count = 1;
      if(!ret.argv[1].empty() && (!fromString(ret.argv[1], count) || count==0))
        return false;
      return giveItem(*world, *player, ret.argv[0], count, false);
      }
    case C_Equip: {
      World* world  = Gothic::inst().world();
      Npc*   player = Gothic::inst().player();
      if(world==nullptr || player==nullptr)
        return false;
      return giveItem(*world, *player, ret.argv[0], 1, true);
      }
    case C_SaveGame: {
      World* world = Gothic::inst().world();
      int    slot  = 0;
      if(world==nullptr || !fromString(ret.argv[0], slot) || slot<0)
        return false;
      return saveGame(*world, slot);
      }
    case C_Screenshot:
      return screenshot(ret.argv[0]);
    case C_ToggleFightLog:
      FightLog::setEnabled(!FightLog::isEnabled());
      print(FightLog::isEnabled() ? "fightlog on" : "fightlog off");
      return true;
    case C_InfoTold: {
      World* world  = Gothic::inst().world();
      Npc*   player = Gothic::inst().player();
      if(world==nullptr || player==nullptr)
        return false;
      if(!world->script().markInfoKnown(*player, world->script().findSymbolIndex(ret.argv[0]))) {
        print(string_frm("info told: \"",ret.argv[0],"\" is not a dialog info"));
        return false;
        }
      return true;
      }
    case C_Immortal: {
      // npc keeps its hit points, so a fight between npcs lasts as long as a test needs
      World* world = Gothic::inst().world();
      Npc*   npc   = world!=nullptr ? findNpc(*world, ret.argv[0]) : nullptr;
      if(npc==nullptr) {
        print(string_frm("immortal: no npc \"",ret.argv[0],"\""));
        return false;
        }
      npc->handle().flags = npc->handle().flags | zenkit::NpcFlag::IMMORTAL;
      return true;
      }
    case C_RemoveNpc: {
      // monsters around a test place would join the fight
      World* world  = Gothic::inst().world();
      Npc*   player = Gothic::inst().player();
      if(world==nullptr || player==nullptr)
        return false;
      return removeNpc(*world, *player, ret.argv[0], ret.argv[1]);
      }
    case C_Quit:
      Tempest::SystemApi::exit();
      return true;
    case C_SetTime: {
      World* world = Gothic::inst().world();
      if(world==nullptr)
        return false;
      return setTime(*world, ret.argv[0], ret.argv[1]);
      }
    case C_PrintVar: {
      World* world  = Gothic::inst().world();
      if(world==nullptr)
        return false;
      return printVariable(world, ret.argv[0]);
      }

    case C_SetVar: {
      World* world  = Gothic::inst().world();
      Npc*   player = Gothic::inst().player();
      if(world==nullptr || player==nullptr)
        return false;
      return setVariable(world, ret.argv[0], ret.argv[1]);
      }

    case C_Call: {
      World* world  = Gothic::inst().world();
      Npc*   player = Gothic::inst().player();
      if(world==nullptr || player==nullptr)
        return false;
      return callFunction(*world, ret.argv[0], ret.argv[1]);
      }

    case C_PlayAni: {
      Npc*   player = Gothic::inst().player();
      if(player==nullptr)
        return false;
      return player->playAnimByName(ret.argv[0], BS_NONE) != nullptr;
      }
    case C_PlayAniNpc: {
      World* world = Gothic::inst().world();
      if(world==nullptr)
        return false;
      return playAni(*world, ret.argv[0], ret.argv[1]);
      }
    case C_AniInfo: {
      World* world = Gothic::inst().world();
      if(world==nullptr)
        return false;
      return aniInfo(*world, ret.argv[0], ret.argv[1]);
      }

    case C_ToggleGI:
      Gothic::inst().toggleGi();
      return true;
    case C_ToggleVsm:
      Gothic::inst().toggleVsm();
      return true;
    case C_ToggleRtsm:
      Gothic::inst().toggleRtsm();
      return true;
    case C_TogglePathtrace:
      Gothic::inst().togglePathtrace();
      return true;
    }

  return true;
  }

bool Marvin::addItemOrNpcBySymbolName(World* world, std::string_view name, const Tempest::Vec3& at) {
  auto&  sc  = world->script();
  size_t id  = sc.findSymbolIndex(name);
  if(id==size_t(-1))
    return false;

  auto*  sym = sc.findSymbol(id);
  if(sym==nullptr || sym->parent()==uint32_t(-1))
    return false;

  if(sym->type()!=zenkit::DaedalusDataType::INSTANCE || sym->address()==0)
    return false;

  const auto* cls = sym;
  while(cls!=nullptr && cls->parent()!=uint32_t(-1)) {
    cls = sc.findSymbol(cls->parent());
    }

  if(cls==nullptr)
    return false;

  if(cls->name()=="C_NPC")
    return (world->addNpc(id, at)!=nullptr);
  if(cls->name()=="C_ITEM")
    return (world->addItem(id, at)!=nullptr);
  return false;
  }

bool Marvin::printVariable(World* world, std::string_view name) {
  string_frm buf;
  auto&  sc  = world->script();
  auto*  sym = sc.findSymbol(name);
  if(sym==nullptr)
    return false;
  switch(sym->type()) {
    case zenkit::DaedalusDataType::INT:
      buf = string_frm(name," = ",sym->get_int(0));
      break;
    case zenkit::DaedalusDataType::FLOAT:
      buf = string_frm(name," = ",sym->get_float(0));
      break;
    case zenkit::DaedalusDataType::STRING:
      buf = string_frm(name," = ",sym->get_string(0));
      break;
    case zenkit::DaedalusDataType::INSTANCE:
      buf = string_frm(name," = ",sym->get_instance().get());
      break;
    default:
      break;
    }
  print(buf);
  return true;
  }

bool Marvin::setVariable(World* world, std::string_view name, std::string_view value) {
  auto&  sc  = world->script();
  auto*  sym = sc.findSymbol(name);
  if(sym==nullptr)
    return false;
  switch(sym->type()) {
    case zenkit::DaedalusDataType::INT: {
      int32_t valueI = 0;
      if(!fromString(value, valueI))
        return false;
      sym->set_int(valueI);
      break;
      }
    case zenkit::DaedalusDataType::FLOAT: {
      float valueF = 0;
      if(!fromString(value, valueF))
        return false;
      sym->set_float(valueF);
      break;
      }
    case zenkit::DaedalusDataType::STRING:
      sym->set_string(value);
      break;
    case zenkit::DaedalusDataType::INSTANCE:
      print("unable to override instance variable");
      break;
    default:
      return false;
    }
  printVariable(world, name);
  return true;
  }

bool Marvin::setTime(World& world, std::string_view hh, std::string_view mm) {
  int hv = 0, mv = 0;

  auto err = std::from_chars(hh.data(), hh.data()+hh.size(), hv, 10).ec;
  if(err!=std::errc())
    return false;

  err = std::from_chars(mm.data(), mm.data()+mm.size(), mv, 10).ec;
  if(err!=std::errc()) {
    mv = 0;
    }

  if(hv<0 || hv>=24 || mv<0 || mv>=60)
    return false;

  world.setDayTime(hv,mv);
  return true;
  }

bool Marvin::goToVob(World& world, Npc& player, Camera& c, std::string_view name, size_t n) {
  auto&  sc = world.script();
  size_t id = sc.findSymbolIndex(name);
  if(id==size_t(-1))
    return false;

  Tempest::Vec3 pos;
  if(auto npc = world.findNpcByInstance(id,n))
     pos = npc->position();
  else if(auto it = world.findItemByInstance(id,n))
     pos = it->position();
  else
    return false;

  if(!player.setInteraction(nullptr))
    return false;
  player.setPosition(pos);
  player.updateTransform();
  c.reset();
  return true;
  }

bool Marvin::callFunction(World& world, std::string_view name, std::string_view args) {
  auto& sc = world.script();
  auto& vm = sc.getVm();
  auto* fn = sc.findSymbol(name);
  if(fn==nullptr || fn->type()!=zenkit::DaedalusDataType::FUNCTION) {
    print(string_frm("call: \"",name,"\" is not a script function"));
    return false;
    }
  if(fn->is_external()) {
    // externals are dispatched only by the BE opcode
    print(string_frm("call: \"",name,"\" is an engine external"));
    return false;
    }

  std::vector<std::string_view> argv;
  for(size_t i=0; i<args.size();) {
    size_t e = args.find(' ',i);
    if(e==std::string_view::npos)
      e = args.size();
    if(e>i)
      argv.push_back(args.substr(i,e-i));
    i = e+1;
    }

  auto params = vm.find_parameters_for_function(fn);
  if(params.size()!=argv.size()) {
    print(string_frm("call: ",fn->name()," expects ",params.size()," arguments, given ",argv.size()));
    return false;
    }

  struct Arg {
    int32_t                                   i = 0;
    float                                     f = 0;
    std::shared_ptr<zenkit::DaedalusInstance> inst;
    };
  std::vector<Arg> val(params.size());
  for(size_t i=0; i<params.size(); ++i) {
    switch(params[i].type()) {
      case zenkit::DaedalusDataType::INT:
      case zenkit::DaedalusDataType::FUNCTION:
        if(!intArgument(world, argv[i], val[i].i)) {
          print(string_frm("call: \"",argv[i],"\" is not a number, constant or instance"));
          return false;
          }
        break;
      case zenkit::DaedalusDataType::FLOAT: {
        auto err = std::from_chars(argv[i].data(), argv[i].data()+argv[i].size(), val[i].f).ec;
        if(err!=std::errc()) {
          print(string_frm("call: \"",argv[i],"\" is not a number"));
          return false;
          }
        break;
        }
      case zenkit::DaedalusDataType::STRING:
        break;
      case zenkit::DaedalusDataType::INSTANCE: {
        auto npc = findNpc(world, argv[i]);
        if(npc==nullptr) {
          print(string_frm("call: no npc \"",argv[i],"\""));
          return false;
          }
        val[i].inst = npc->handlePtr();
        break;
        }
      default:
        print(string_frm("call: unsupported parameter ",params[i].name()));
        return false;
      }
    }

  struct ScopeVar final {
    ScopeVar(zenkit::DaedalusSymbol* sym, const std::shared_ptr<zenkit::DaedalusInstance>& h) : sym(sym) {
      if(sym==nullptr)
        return;
      prev = sym->get_instance();
      sym->set_instance(h);
      }
    ~ScopeVar() {
      if(sym!=nullptr)
        sym->set_instance(prev);
      }
    zenkit::DaedalusSymbol*                   sym = nullptr;
    std::shared_ptr<zenkit::DaedalusInstance> prev;
    };

  Npc*     player = Gothic::inst().player();
  Npc*     target = player->target();
  ScopeVar self (vm.global_self(),  player->handlePtr());
  ScopeVar other(vm.global_other(), target!=nullptr ? target->handlePtr() : player->handlePtr());

  try {
    for(size_t i=0; i<params.size(); ++i) {
      switch(params[i].type()) {
        case zenkit::DaedalusDataType::INT:
        case zenkit::DaedalusDataType::FUNCTION:
          vm.push_int(val[i].i);
          break;
        case zenkit::DaedalusDataType::FLOAT:
          vm.push_float(val[i].f);
          break;
        case zenkit::DaedalusDataType::STRING:
          vm.push_string(argv[i]);
          break;
        default:
          vm.push_instance(val[i].inst);
          break;
        }
      }
    vm.unsafe_call(fn);

    if(!fn->has_return()) {
      print(string_frm("call: ",fn->name()," done"));
      return true;
      }
    switch(fn->rtype()) {
      case zenkit::DaedalusDataType::INT:
        print(string_frm("call: ",fn->name()," = ",vm.pop_int()));
        break;
      case zenkit::DaedalusDataType::FLOAT:
        print(string_frm("call: ",fn->name()," = ",vm.pop_float()));
        break;
      case zenkit::DaedalusDataType::STRING:
        print(string_frm("call: ",fn->name()," = ",std::string_view(vm.pop_string())));
        break;
      default:
        print(string_frm("call: ",fn->name()," = ",vm.pop_instance().get()));
        break;
      }
    }
  catch(const std::exception& e) {
    print(string_frm("call: ",fn->name(),": ",e.what()));
    return false;
    }
  return true;
  }

bool Marvin::intArgument(World& world, std::string_view arg, int32_t& v) {
  auto err = std::from_chars(arg.data(), arg.data()+arg.size(), v).ec;
  if(err==std::errc())
    return true;

  // constant or instance name
  auto* sym = world.script().findSymbol(arg);
  if(sym==nullptr)
    return false;
  if(sym->type()==zenkit::DaedalusDataType::INT && !sym->is_member()) {
    v = sym->get_int(0);
    return true;
    }
  if(sym->type()==zenkit::DaedalusDataType::INSTANCE || sym->type()==zenkit::DaedalusDataType::FUNCTION) {
    v = int32_t(sym->index());
    return true;
    }
  return false;
  }

static std::string toUpper(std::string_view s) {
  std::string ret(s);
  for(auto& c:ret)
    c = char(std::toupper(uint8_t(c)));
  return ret;
  }

static std::string number(double v) {
  char buf[32] = {};
  std::snprintf(buf,sizeof(buf),"%g",v);
  return buf;
  }

// one line of 'ani info': the tokens that are not empty, separated by a space
static std::string join(std::initializer_list<std::string> tokens) {
  std::string ret;
  for(auto& t:tokens) {
    if(t.empty())
      continue;
    if(!ret.empty())
      ret += ' ';
    ret += t;
    }
  return ret;
  }

static const char* eventName(zenkit::MdsEventType t) {
  using E = zenkit::MdsEventType;
  switch(t) {
    case E::ITEM_CREATE:       return "DEF_CREATE_ITEM";
    case E::ITEM_INSERT:       return "DEF_INSERT_ITEM";
    case E::ITEM_REMOVE:       return "DEF_REMOVE_ITEM";
    case E::ITEM_DESTROY:      return "DEF_DESTROY_ITEM";
    case E::ITEM_PLACE:        return "DEF_PLACE_ITEM";
    case E::ITEM_EXCHANGE:     return "DEF_EXCHANGE_ITEM";
    case E::SET_FIGHT_MODE:    return "DEF_FIGHTMODE";
    case E::MUNITION_PLACE:    return "DEF_PLACE_MUNITION";
    case E::MUNITION_REMOVE:   return "DEF_REMOVE_MUNITION";
    case E::SOUND_DRAW:        return "DEF_DRAWSOUND";
    case E::SOUND_UNDRAW:      return "DEF_UNDRAWSOUND";
    case E::MESH_SWAP:         return "DEF_SWAPMESH";
    case E::TORCH_DRAW:        return "DEF_DRAWTORCH";
    case E::TORCH_INVENTORY:   return "DEF_INV_TORCH";
    case E::TORCH_DROP:        return "DEF_DROP_TORCH";
    case E::HIT_LIMB:          return "DEF_HIT_LIMB";
    case E::HIT_DIRECTION:     return "DEF_DIR";
    case E::DAMAGE_MULTIPLIER: return "DEF_DAM_MULTIPLY";
    case E::PARRY_FRAME:       return "DEF_PAR_FRAME";
    case E::OPTIMAL_FRAME:     return "DEF_OPT_FRAME";
    case E::HIT_END:           return "DEF_HIT_END";
    case E::COMBO_WINDOW:      return "DEF_WINDOW";
    case E::UNKNOWN:           break;
    }
  return "UNKNOWN";
  }

static const char* fightModeName(zenkit::MdsFightMode m) {
  using M = zenkit::MdsFightMode;
  switch(m) {
    case M::FIST:          return "FIST";
    case M::SINGLE_HANDED: return "1H";
    case M::DUAL_HANDED:   return "2H";
    case M::BOW:           return "BOW";
    case M::CROSSBOW:      return "CBOW";
    case M::MAGIC:         return "MAG";
    case M::NONE:          return "NONE";
    case M::INVALID:       break;
    }
  return "";
  }

bool Marvin::playAni(World& world, std::string_view who, std::string_view name) {
  Npc* npc = findNpc(world, who);
  if(npc==nullptr) {
    print(string_frm("play ani: no npc \"",who,"\""));
    return false;
    }
  const auto ani = toUpper(name);
  if(npc->animSequence(ani)==nullptr) {
    print(string_frm("play ani: \"",who,"\" has no animation \"",name,"\""));
    return false;
    }
  if(npc->playAnimByName(ani, BS_NONE)==nullptr) {
    print(string_frm("play ani: \"",who,"\" cannot start \"",name,"\" now"));
    return false;
    }
  return true;
  }

// The definition of an animation as the model of the npc holds it after loading (overlays first),
// in the format of tools/anim.py defs (spec 004 W9): origin, layer, flags, frame range, MAN frames,
// next and events.
bool Marvin::aniInfo(World& world, std::string_view who, std::string_view name) {
  Npc* npc = findNpc(world, who);
  if(npc==nullptr) {
    print(string_frm("ani info: no npc \"",who,"\""));
    return false;
    }
  auto sq = npc->animSequence(toUpper(name));
  if(sq==nullptr || sq->data==nullptr) {
    print(string_frm("ani info: \"",who,"\" has no animation \"",name,"\""));
    return false;
    }

  using F = zenkit::AnimationFlags;
  const std::pair<F,char> letters[] = {{F::MOVE,'M'},{F::ROTATE,'R'},{F::QUEUE,'E'},{F::FLY,'F'},{F::IDLE,'I'},{F::INPLACE,'P'}};
  std::string flags;
  for(auto& [f,c]:letters)
    if(sq->flags & f)
      flags.push_back(c);

  const auto& d = *sq->data;
  print(join({"ani", sq->name, "origin", sq->extension ? "mod" : "game", "layer", std::to_string(sq->layer),
              "next", sq->next.empty() ? "-" : sq->next,
              "blend", number(double(sq->blendIn)/1000.0), number(double(sq->blendOut)/1000.0),
              "flags", flags.empty() ? "-" : flags, "dir", sq->reverse ? "R" : "F",
              "frames", std::to_string(d.firstFrame)+"-"+std::to_string(d.lastFrame),
              "fps", number(d.fpsRate), "man", std::to_string(d.numFrames)}));

  for(auto& e:d.events) {
    std::string frames;
    for(auto f:e.frames)
      frames += (frames.empty() ? "frames=" : ",") + std::to_string(f);
    const bool mode = e.type==zenkit::MdsEventType::SET_FIGHT_MODE && e.fight_mode!=zenkit::MdsFightMode::INVALID;
    print("  " + join({"tag", std::to_string(e.frame), eventName(e.type),
                       e.slot .empty() ? "" : "slot=" +toUpper(e.slot),
                       e.slot2.empty() ? "" : "slot2="+toUpper(e.slot2),
                       e.item .empty() ? "" : "item=" +toUpper(e.item),
                       mode ? std::string("mode=")+fightModeName(e.fight_mode) : "",
                       frames}));
    }
  for(auto& s:d.sfx)
    print("  " + join({"sfx", std::to_string(s.frame), toUpper(s.name), "range="+number(s.range), s.empty_slot ? "empty" : ""}));
  for(auto& s:d.gfx)
    print("  " + join({"sfxground", std::to_string(s.frame), toUpper(s.name)}));
  for(auto& p:d.pfx)
    if(!p.pfxStop)
      print("  " + join({"pfx", std::to_string(p.frame), std::to_string(p.index), toUpper(p.name), toUpper(p.position),
                         p.attached ? "attach" : ""}));
  for(auto& p:d.pfx)
    if(p.pfxStop)
      print("  " + join({"pfxstop", std::to_string(p.frame), std::to_string(p.index)}));
  for(auto& m:d.mmStartAni)
    print("  " + join({"morph", std::to_string(m.frame), toUpper(m.animation), toUpper(m.node)}));
  return true;
  }

Npc* Marvin::findNpc(World& world, std::string_view name) {
  if(compareNoCase(name,"hero"))
    return Gothic::inst().player();

  size_t id = world.script().findSymbolIndex(name);
  if(id==size_t(-1))
    return nullptr;

  // the most recently added npc of this instance, e.g. the one from 'insert'
  Npc* ret = nullptr;
  for(size_t n=0; auto npc = world.findNpcByInstance(id,n); ++n)
    ret = npc;
  return ret;
  }

bool Marvin::removeNpc(World& world, Npc& player, std::string_view name, std::string_view radius) {
  size_t id = world.script().findSymbolIndex(name);
  size_t r  = 0;
  if(id==size_t(-1) || !fromString(radius, r))
    return false;

  std::vector<Npc*> npc;
  world.detectNpc(player.position(), float(r)*100.f, [&](Npc& n) {
    if(n.instanceSymbol()==id && &n!=&player)
      npc.push_back(&n);
    });
  // an empty result means a wrong place or name, which a scenario should report
  if(npc.empty()) {
    print(string_frm("remove npc: no \"",name,"\" within ",int(r)," m"));
    return false;
    }
  for(auto i:npc)
    world.removeNpc(*i);
  print(string_frm("remove npc: ",int(npc.size())," removed"));
  return true;
  }

bool Marvin::giveItem(World& world, Npc& player, std::string_view name, size_t count, bool equip) {
  auto&  sc  = world.script();
  size_t id  = sc.findSymbolIndex(name);
  auto*  cls = id==size_t(-1) ? nullptr : sc.findSymbol(id);
  if(cls!=nullptr && (cls->type()!=zenkit::DaedalusDataType::INSTANCE || cls->address()==0))
    cls = nullptr;
  while(cls!=nullptr && cls->parent()!=uint32_t(-1))
    cls = sc.findSymbol(cls->parent());
  if(cls==nullptr || cls->name()!="C_ITEM") {
    print(string_frm("\"",name,"\" is not an item"));
    return false;
    }

  if(!equip) {
    player.addItem(id, count);
    return true;
    }
  if(player.itemCount(id)==0)
    player.addItem(id, 1);
  player.useItem(id, Item::NSLOT, true);
  return true;
  }

bool Marvin::saveGame(World& world, int slot) {
  // MainWindow::saveGame silently skips these cases
  if(Gothic::inst().checkLoading()!=Gothic::LoadState::Idle || Gothic::inst().isInDialog() || world.currentCs()!=nullptr) {
    print("save game: not possible during loading, a dialog or a cutscene");
    return false;
    }
  string_frm file("save_slot_",slot,".sav");
  Gothic::inst().save(file, string_frm("Console save ",slot));
  print(string_frm("save game: ",std::string_view(file)));
  return true;
  }

bool Marvin::screenshot(std::string_view name) {
  if(Gothic::inst().world()==nullptr)
    return false;
  auto file = CommandLine::inst().resultsFile(name);
  auto path = Tempest::TextCodec::toUtf8(file);

  std::error_code ec;
  std::filesystem::remove(file, ec);
  Gothic::inst().onScreenshot(path);
  if(!std::filesystem::exists(file, ec)) {
    print(string_frm("screenshot: unable to write \"",path,"\""));
    return false;
    }
  print(string_frm("screenshot: ",path));
  return true;
  }

std::string_view Marvin::completeInstanceName(std::string_view inp, bool& fullword) const {
  World* world  = Gothic::inst().world();
  if(world==nullptr || inp.size()==0)
    return "";

  auto&            sc    = world->script();
  std::string_view match = "";
  for(size_t i=0; i<sc.symbolsCount(); ++i) {
    auto*  sym  = sc.findSymbol(i);
    auto   name = std::string_view(sym->name());
    if(!startsWith(name,inp))
      continue;

    if(match.empty()) {
      match   = name;
      fullword = true;
      continue;
      }
    if(name.size()>match.size())
      name = name.substr(0,match.size());
    for(size_t i=0; i<name.size(); ++i) {
      int n = std::tolower(name [i]);
      int m = std::tolower(match[i]);
      if(m!=n) {
        name     = name.substr(0,i);
        fullword = false;
        break;
        }
      }
    match = name;
    }
  return match;
  }
