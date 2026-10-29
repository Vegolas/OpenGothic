#include "fightlog.h"

#include <Tempest/Log>
#include <Tempest/TextCodec>

#include <cstdio>
#include <filesystem>
#include <fstream>
#include <memory>
#include <string>
#include <unordered_map>

#include "game/fightalgo.h"
#include "world/objects/npc.h"
#include "world/world.h"
#include "commandline.h"
#include "gothic.h"

using namespace Tempest;

namespace {

// One JSON object. Bytes outside of ASCII are written as \u00XX: script strings use a legacy codepage.
class Json final {
  public:
    Json(uint64_t t, std::string_view ev) {
      num("t",int64_t(t));
      str("ev",ev);
      }

    Json& num(std::string_view k, int64_t v) {
      key(k);
      s += std::to_string(v);
      return *this;
      }

    Json& str(std::string_view k, std::string_view v) {
      key(k);
      text(v);
      return *this;
      }

    Json& flag(std::string_view k, bool v) {
      key(k);
      s += v ? "true" : "false";
      return *this;
      }

    Json& null(std::string_view k) {
      key(k);
      s += "null";
      return *this;
      }

    const std::string& done() {
      s.push_back('}');
      return s;
      }

  private:
    void key(std::string_view k) {
      if(s.size()>1)
        s.push_back(',');
      text(k);
      s.push_back(':');
      }

    void text(std::string_view v) {
      s.push_back('"');
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
      }

    std::string s = "{";
  };

struct Character final {
  uint32_t                    id      = 0;
  uint32_t                    attacks = 0;
  std::weak_ptr<zenkit::INpc> handle;
  };

std::ofstream                             out;
bool                                      opened = false;
uint32_t                                  lastId = 0;
std::unordered_map<const Npc*,Character>  characters;

uint64_t worldTime() {
  auto w = Gothic::inst().world();
  return w!=nullptr ? w->tickCount() : 0;
  }

void write(const std::string& line) {
  if(!opened)
    return;
  out << line << '\n';
  out.flush();
  }

Character& character(Npc& npc) {
  // npc objects are recreated on load: a new handle at the same address gets a new id
  auto& c = characters[&npc];
  if(c.id==0 || c.handle.lock()!=npc.handlePtr()) {
    c        = Character();
    c.id     = ++lastId;
    c.handle = npc.handlePtr();
    }
  return c;
  }

std::string_view instanceName(Npc& npc) {
  auto sym = npc.world().script().findSymbol(size_t(npc.instanceSymbol()));
  return sym!=nullptr ? std::string_view(sym->name()) : std::string_view();
  }

void who(Json& j, Npc& npc, const Character& c) {
  j.str("who",instanceName(npc)).num("who_id",c.id).flag("player",npc.isPlayer());
  }

std::string_view moveName(zenkit::FightAiMove mv) {
  using zenkit::FightAiMove;
  switch(mv) {
    case FightAiMove::ATTACK:        return "attack";
    case FightAiMove::ATTACK_SIDE:   return "side";
    case FightAiMove::ATTACK_FRONT:  return "front";
    case FightAiMove::ATTACK_TRIPLE: return "triple";
    case FightAiMove::ATTACK_WHIRL:  return "whirl";
    case FightAiMove::ATTACK_MASTER: return "master";
    default:
      return "other";
    }
  }

void open() {
  if(opened)
    return;
  auto file = CommandLine::inst().resultsFile("fightlog.jsonl");
  out.open(std::filesystem::path(file), std::ios::binary | std::ios::trunc);
  if(!out) {
    Log::e("fightlog: unable to open \"",TextCodec::toUtf8(file),"\"");
    return;
    }
  opened = true;

  Json j(worldTime(),"meta");
  j.num("format",1);
  if(auto w = Gothic::inst().world())
    j.str("world",w->name()); else
    j.null("world");
  auto mod = std::filesystem::path(CommandLine::inst().modPath()).filename();
  if(!mod.empty())
    j.str("mod",TextCodec::toUtf8(mod.u16string())); else
    j.null("mod");
  write(j.done());
  }
}

void FightLog::setEnabled(bool e) {
  if(e==enabled)
    return;
  if(e) {
    if(!CommandLine::inst().isDevMode())
      return;
    open();
    if(!opened)
      return;
    enabled = true;
    marker("fightlog_on");
    } else {
    marker("fightlog_off");
    enabled = false;
    }
  }

void FightLog::attack(Npc& npc, AnimationSolver::Anim anim, BodyState bs, const Pose::ComboStart& cs,
                      uint16_t comboLen, const FightAlgo& fai) {
  if(!enabled)
    return;

  std::string_view weapon = "other";
  Talent           tal    = TALENT_UNKNOWN;
  switch(npc.weaponState()) {
    case WeaponState::Fist: weapon = "fist";                  break;
    case WeaponState::W1H:  weapon = "1h"; tal = TALENT_1H;   break;
    case WeaponState::W2H:  weapon = "2h"; tal = TALENT_2H;   break;
    default:
      // melee only
      return;
    }

  if(cs.broken>0) {
    auto& c = character(npc);
    Json  j(npc.world().tickCount(),"break");
    who(j,npc,c);
    j.str("what","combo").str("why",cs.link==Pose::CL_Block ? "block" : "no_window");
    j.null("series").null("series_id").num("series_pos",cs.broken);
    write(j.done());
    }

  if(bs==BS_PARADE || anim==AnimationSolver::AttackBlock)
    return;

  std::string_view link;
  switch(cs.link) {
    case Pose::CL_New:     link = "new";  break;
    case Pose::CL_Forward: link = "fwd";  break;
    case Pose::CL_Side:    link = "side"; break;
    default:
      // no new hit
      return;
    }

  std::string_view dir = "other";
  switch(anim) {
    case AnimationSolver::Attack:       dir = (bs==BS_RUN ? "run" : "fwd"); break;
    case AnimationSolver::AttackL:      dir = "left";   break;
    case AnimationSolver::AttackR:      dir = "right";  break;
    case AnimationSolver::AttackFinish: dir = "finish"; break;
    default:
      break;
    }

  // queued attacks are consumed after the swing, so the queue still holds this one
  std::string_view src = "other";
  if(npc.isPlayer())
    src = "player";
  else if(fai.hasInstructions())
    src = "queue";
  else if(anim!=AnimationSolver::AttackFinish)
    src = "continue";

  auto& c   = character(npc);
  auto  tgt = npc.target();
  c.attacks++;

  Json j(npc.world().tickCount(),"attack");
  who(j,npc,c);
  j.num("n",c.attacks).str("name",npc.displayName());
  if(tgt!=nullptr) {
    auto& t = character(*tgt);
    j.str("tgt",instanceName(*tgt)).num("tgt_id",t.id).flag("tgt_down",tgt->isDown());
    } else {
    j.null("tgt").null("tgt_id").flag("tgt_down",false);
    }
  j.num("tactic",npc.handle().fight_tactic).str("weapon",weapon);
  j.num("talent",    tal!=TALENT_UNKNOWN ? npc.talentSkill(tal) : 0);
  j.num("talent_pct",tal!=TALENT_UNKNOWN ? npc.hitChance(tal)   : 0);
  j.str("dir",dir).num("combo",cs.link==Pose::CL_Forward ? comboLen+1 : 1).str("link",link);
  if(cs.window>=0)
    j.num("win_pct",cs.window); else
    j.null("win_pct");
  j.num("skip_ms",int64_t(cs.skip)).str("src",src);

  const auto& ser = fai.series();
  if(src=="queue" && ser.len>0) {
    j.str("series",moveName(ser.move)).num("series_id",ser.id).num("series_pos",ser.done+1).num("series_len",ser.len);
    }
  else if(src=="continue") {
    j.str("series","combo").null("series_id").null("series_pos").null("series_len");
    }
  else {
    j.null("series").null("series_id").null("series_pos").null("series_len");
    }
  write(j.done());

  Event e;
  e.npc   = &npc;
  e.type  = "attack";
  e.combo = (cs.link==Pose::CL_Forward ? comboLen+1 : 1);
  if(src=="queue" && ser.len>0) {
    e.seriesPos = ser.done+1;
    e.seriesLen = ser.len;
    }
  onEvent(e);
  }

static void result(Npc& npc, Npc* tgt, std::string_view res, std::string_view why, uint16_t comboLen,
                   int32_t dmg, int32_t hpBefore, int32_t hpAfter, bool stagger) {
  switch(npc.weaponState()) {
    case WeaponState::Bow:
    case WeaponState::CBow:
    case WeaponState::Mage:
      // melee only
      return;
    default:
      break;
    }

  auto& c = character(npc);
  Json  j(npc.world().tickCount(),"result");
  who(j,npc,c);
  j.num("n",c.attacks);
  if(tgt!=nullptr) {
    auto& t = character(*tgt);
    j.str("tgt",instanceName(*tgt)).num("tgt_id",t.id);
    } else {
    j.null("tgt").null("tgt_id");
    }
  j.str("res",res);
  if(!why.empty())
    j.str("why",why); else
    j.null("why");
  j.num("combo",comboLen+1).num("dmg",dmg).num("hp_before",hpBefore).num("hp_after",hpAfter).flag("stagger",stagger);
  write(j.done());
  }

void FightLog::miss(Npc& npc, Npc* tgt, std::string_view why, uint16_t comboLen) {
  if(!enabled)
    return;
  result(npc,tgt,"miss",why,comboLen,0,0,0,false);
  }

void FightLog::defend(Npc& npc, Npc& tgt, bool jumpBack, uint16_t comboLen) {
  if(!enabled)
    return;
  result(npc,&tgt,jumpBack ? "jumpback" : "block","",comboLen,0,0,0,false);
  }

void FightLog::hit(Npc& npc, Npc& tgt, uint16_t comboLen, int32_t dmg, int32_t hpBefore, bool stagger) {
  if(!enabled)
    return;
  result(npc,&tgt,"hit","",comboLen,dmg,hpBefore,tgt.attribute(ATR_HITPOINTS),stagger);
  }

void FightLog::state(Npc& npc, std::string_view st, Npc* by) {
  if(!enabled)
    return;
  auto& c = character(npc);
  Json  j(npc.world().tickCount(),"state");
  who(j,npc,c);
  j.str("state",st);
  if(by!=nullptr) {
    auto& b = character(*by);
    j.str("by",instanceName(*by)).num("by_id",b.id);
    } else {
    j.null("by").null("by_id");
    }
  write(j.done());

  Event e;
  e.npc   = &npc;
  e.type  = "state";
  e.state = st;
  onEvent(e);
  }

void FightLog::seriesBreak(Npc& npc, const FightAlgo::Series& ser, bool queued, std::string_view why) {
  if(!enabled)
    return;
  auto& c = character(npc);
  Json  j(npc.world().tickCount(),"break");
  who(j,npc,c);
  j.str("what","series").str("why",why);
  if(queued && ser.len>0)
    j.str("series",moveName(ser.move)).num("series_id",ser.id).num("series_pos",ser.done); else
    j.str("series","combo").null("series_id").null("series_pos");
  write(j.done());
  }

void FightLog::marker(std::string_view what, int32_t line, std::string_view text, std::string_view file) {
  if(!enabled)
    return;
  Json j(worldTime(),"marker");
  j.str("what",what);
  if(line>=0)
    j.num("line",line); else
    j.null("line");
  j.str("text",text);
  if(!file.empty())
    j.str("file",file); else
    j.null("file");
  write(j.done());
  }
