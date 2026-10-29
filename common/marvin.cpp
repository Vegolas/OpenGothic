#include "marvin.h"

#include <Tempest/SystemApi>

#include <charconv>
#include <cstdint>
#include <cctype>

#include "utils/string_frm.h"
#include "world/objects/npc.h"
#include "world/objects/item.h"
#include "world/triggers/abstracttrigger.h"
#include "camera.h"
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
    {"play ani %s",                C_PlayAni},
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
      return addItemOrNpcBySymbolName(world, ret.argv[0], player->position());
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
