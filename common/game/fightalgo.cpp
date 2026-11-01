#include "fightalgo.h"

#include <Tempest/Log>

#include "game/definitions/fightaidefinitions.h"
#include "world/objects/npc.h"
#include "world/objects/item.h"
#include "gothic.h"
#include "serialize.h"

// According to Gothic1 scripts:
// W  - Weapon Range (FIGHT_RANGE_FIST * 3)
// G  - Walking range (3 * W). Buffer for ranged fighters in which they should switch to a melee weapon.
// FK - Long-range combat range (30m)

FightAlgo::FightAlgo() {
  }

void FightAlgo::load(Serialize &fin) {
  fin.read(reinterpret_cast<int32_t&>(queueId));
  for(int i=0;i<MV_MAX;++i)
    fin.read(reinterpret_cast<uint8_t&>(tr[i]));
  fin.read(hitFlg);
  }

void FightAlgo::save(Serialize &fout) {
  fout.write(int32_t(queueId));
  for(int i=0;i<MV_MAX;++i)
    fout.write(uint8_t(tr[i]));
  fout.write(hitFlg);
  }

void FightAlgo::fillQueue(Npc &npc, Npc &tg, GameScript& owner) {
  auto& ai = Gothic::fai()[size_t(npc.handle().fight_tactic)];
  auto  ws = npc.weaponState();

  if(hitFlg) {
    hitFlg = false;
    if(fillQueue(owner,ai.my_w_strafe))
      return;
    }

  const bool focus = isInFocusAngle(npc,tg);

  if(isEnemyPrehit(npc,tg,owner)){
    if(tg.bodyStateMasked()==BS_RUN)
      if(fillQueue(owner,ai.enemy_stormprehit))
        return;
    if(fillQueue(owner,ai.enemy_prehit))
      return;
    }

  if(ws==WeaponState::Fist || ws==WeaponState::W1H || ws==WeaponState::W2H) {
    if(isInWRange(npc,tg,owner)) {
      if(focus && npc.bodyStateMasked()==BS_RUN)
        if(fillQueue(owner,ai.my_w_runto))
          return;
      if(focus && npc.bodyStateMasked()!=BS_RUN)
        if(fillQueue(owner,ai.my_w_focus))
          return;
      if(fillQueue(owner,ai.my_w_nofocus))
        return;
      }

    if(isInGRange(npc,tg,owner)) {
      if(focus && npc.bodyStateMasked()==BS_RUN)
        if(fillQueue(owner,ai.my_g_runto))
          return;
      if(focus && npc.bodyStateMasked()!=BS_RUN)
        if(fillQueue(owner,ai.my_g_focus))
          return;
      }
    }

  if(ws==WeaponState::Mage) {
    if(isInWRange(npc,tg,owner))
      if(fillQueue(owner,ai.my_fk_focus_mag))
        return;
    if(fillQueue(owner,ai.my_fk_nofocus_mag))
      return;
    }

  if(isInWRange(npc,tg,owner) && focus)
    if(fillQueue(owner,ai.my_fk_focus_far))
      return;
  if(fillQueue(owner,ai.my_fk_nofocus_far))
    return;

  fillQueue(owner,ai.my_w_nofocus);
  }

bool FightAlgo::fillQueue(GameScript& owner, const FightAi::Moves& src) {
  const auto mv = randomMove(owner,src);
  if(mv==zenkit::FightAiMove::NOP)
    return false;
  queueId = mv;
  return true;
  }

zenkit::FightAiMove FightAlgo::randomMove(GameScript& owner, const FightAi::Moves& src) {
  uint32_t sz=0;
  for(size_t i=0; i<FightAi::MaxMoves; ++i){
    if(src.move[i]==zenkit::FightAiMove::NOP)
      break;
    sz++;
    }
  if(sz==0)
    return zenkit::FightAiMove::NOP;
  return zenkit::FightAiMove(src.move[owner.rand(sz)]);
  }

FightAlgo::Action FightAlgo::nextFromQueue(Npc& npc, Npc& tg, GameScript& owner) {
  using zenkit::FightAiMove;

  if(tr[0]==MV_NULL) {
    switch(queueId) {
      case FightAiMove::TURN:
        tr[0] = MV_TURN;
        break;
      case FightAiMove::RUN:{
        tr[0] = MV_MOVE;
        break;
        }
      case FightAiMove::RUN_BACK:{
        tr[0] = MV_NULL; //TODO
        break;
        }
      case FightAiMove::JUMP_BACK:{
        tr[0] = MV_JUMPBACK;
        break;
        }
      case FightAiMove::STRAFE:{
        tr[0] = owner.rand(2) ? MV_STRAFEL : MV_STRAFER;
        tr[1] = FightAlgo::MV_STRAFE_E;
        break;
        }
      case FightAiMove::ATTACK:{
        tr[0] = MV_ATTACK;
        break;
        }
      case FightAiMove::ATTACK_SIDE:{
        tr[0] = MV_ATTACKL;
        tr[1] = MV_ATTACKR;
        break;
        }
      case FightAiMove::ATTACK_FRONT:{
        tr[0] = owner.rand(2) ? MV_ATTACKL : MV_ATTACKR;
        tr[1] = MV_ATTACK;
        break;
        }
      case FightAiMove::ATTACK_TRIPLE:{
        if(owner.rand(2)){
          tr[0] = MV_ATTACK;
          tr[1] = MV_ATTACKR;
          tr[2] = MV_ATTACKL;
          } else {
          tr[0] = MV_ATTACKL;
          tr[1] = MV_ATTACKR;
          tr[2] = MV_ATTACK;
          }
        break;
        }
      case FightAiMove::ATTACK_WHIRL:{
        tr[0] = MV_ATTACKL;
        tr[1] = MV_ATTACKR;
        tr[2] = MV_ATTACKL;
        tr[3] = MV_ATTACKR;
        break;
        }
      case FightAiMove::ATTACK_MASTER:{
        tr[0] = MV_ATTACKL;
        tr[1] = MV_ATTACKR;
        tr[2] = MV_ATTACK;
        tr[3] = MV_ATTACK;
        tr[4] = MV_ATTACK;
        tr[5] = MV_ATTACK;
        break;
        }
      case FightAiMove::TURN_TO_HIT:{
        tr[0] = MV_TURN2HIT;
        break;
        }
      case FightAiMove::PARRY:{
        tr[0] = MV_BLOCK;
        break;
        }
      case FightAiMove::STAND_UP:{
        break;
        }
      case FightAiMove::WAIT:
      case FightAiMove::WAIT_EXT:{
        tr[0] = MV_WAIT;
        break;
        }
      case FightAiMove::WAIT_LONGER:{
        tr[0] = MV_WAITLONG;
        break;
        }
      default: {
        static std::set<FightAiMove> inst;
        if(inst.find(queueId)==inst.end()) {
          Tempest::Log::d("unrecognized FAI instruction: ", int(queueId));
          inst.insert(queueId);
          }
        }
      }
    queueId = FightAiMove::NOP;
    }
  return tr[0];
  }

bool FightAlgo::hasInstructions() const {
  return tr[0]!=MV_NULL;
  }

bool FightAlgo::fetchInstructions(Npc &npc, Npc &tg, GameScript& owner) {
  fillQueue(npc,tg,owner);
  if(queueId==zenkit::FightAiMove::NOP)
    return false;
  nextFromQueue(npc,tg,owner);
  return true;
  }

void FightAlgo::consumeAction() {
  for(size_t i=1;i<MV_MAX;++i)
    tr[i-1]=tr[i];
  tr[MV_MAX-1]=MV_NULL;
  }

void FightAlgo::dropForwardAttacks(bool fist) {
  // NOTE: fist has no side attacks - every attack is a forward one
  while(tr[0]==MV_ATTACK || (fist && (tr[0]==MV_ATTACKL || tr[0]==MV_ATTACKR)))
    consumeAction();
  }

void FightAlgo::onClearTarget() {
  queueId = zenkit::FightAiMove::NOP;
  tr[0]   = MV_NULL;
  }

void FightAlgo::onTakeHit() {
  hitFlg = true;
  for(auto& i:tr)
    i = MV_NULL;
  queueId = zenkit::FightAiMove::NOP;
  }

void FightAlgo::onBreakSeries() {
  for(auto& i:tr)
    i = MV_NULL;
  queueId = zenkit::FightAiMove::NOP;
  }

void FightAlgo::onHitFrame() {
  hitLanded = false;
  }

void FightAlgo::onHitLanded() {
  hitLanded = true;
  }

bool FightAlgo::onEnemyPrehit(Npc& npc, Npc& tg, GameScript& owner) {
  // same reaction as in fillQueue, but in the middle of own series
  auto& ai = Gothic::fai()[size_t(npc.handle().fight_tactic)];
  auto  mv = zenkit::FightAiMove::NOP;
  if(tg.bodyStateMasked()==BS_RUN)
    mv = randomMove(owner,ai.enemy_stormprehit);
  if(mv==zenkit::FightAiMove::NOP)
    mv = randomMove(owner,ai.enemy_prehit);
  if(mv==zenkit::FightAiMove::NOP)
    return false;

  onBreakSeries();
  queueId = mv;
  nextFromQueue(npc,tg,owner);
  return true;
  }

float FightAlgo::qDistTo(const Npc& npc, const Npc& tg) const {
  return npc.fightDistanceTo(tg).quadLength();
  }

bool FightAlgo::hasCombo(Npc& npc) const {
  return comboAi(npc).enabled;
  }

const FightAi::Combo& FightAlgo::comboAi(Npc& npc) const {
  return Gothic::fai()[size_t(npc.handle().fight_tactic)].combo;
  }

uint64_t FightAlgo::comboLinkTime(Npc& npc, uint64_t winBegin, uint64_t winEnd, GameScript& owner) {
  // attack layer is removed right after DEF_HIT_END - keep some margin to not miss the window
  static const uint64_t margin = 50;
  if(linkWindow==winBegin)
    return linkTime;

  auto&    cmb = comboAi(npc);
  uint64_t len = (winEnd>winBegin+margin) ? (winEnd-winBegin-margin) : 0;
  uint64_t pc  = uint64_t(cmb.link_min) + owner.rand(uint32_t(cmb.link_max-cmb.link_min+1));

  // NOTE: combo window begin is exclusive
  linkWindow = winBegin;
  linkTime   = winBegin + 1 + len*pc/100;
  return linkTime;
  }

bool FightAlgo::comboContinue(Npc& npc, uint64_t winBegin, GameScript& owner) {
  // 'MOVE_ATTACK in ComboZone = Combo', according to G2 scripts
  if(contWindow==winBegin)
    return contAttack;

  auto& ai = Gothic::fai()[size_t(npc.handle().fight_tactic)];
  contWindow = winBegin;
  contAttack = (randomMove(owner,ai.my_w_combo)==zenkit::FightAiMove::ATTACK);
  return contAttack;
  }

float FightAlgo::baseDistance(const Npc& npc, const Npc& tg,  GameScript &owner) const {
  auto&  gv      = owner.guildVal();
  float  baseTg  = float(gv.fight_range_base[tg .guild()]);
  float  baseNpc = float(gv.fight_range_base[npc.guild()]);
  return baseTg + baseNpc;
  }

float FightAlgo::prefferedAttackDistance(const Npc& npc, const Npc& tg,  GameScript &owner) const {
  auto&  gv      = owner.guildVal();
  float  baseTg  = float(gv.fight_range_base[tg.guild()]);
  float  baseNpc = float(gv.fight_range_base[npc.guild()]);
  return baseTg + baseNpc + weaponRange(owner,npc);
  }

float FightAlgo::prefferedGDistance(const Npc& npc, const Npc& tg, GameScript &owner) const {
  auto   gl      = npc.guild();
  auto&  gv      = owner.guildVal();
  float  baseTg  = float(gv.fight_range_base[tg.guild()]);
  float  baseNpc = float(gv.fight_range_base[npc.guild()]);
  return float(baseTg + baseNpc + float(gv.fight_range_g[gl])) + weaponRange(owner,npc);
  }

float FightAlgo::attackFinishDistance(GameScript &owner) const {
  float NPC_ATTACK_FINISH_DISTANCE = 180;
  if(auto var = owner.findSymbol("NPC_ATTACK_FINISH_DISTANCE")) {
    if(var->type()==zenkit::DaedalusDataType::INT)
      NPC_ATTACK_FINISH_DISTANCE = float(var->get_int());
    else if(var->type()==zenkit::DaedalusDataType::FLOAT)
      NPC_ATTACK_FINISH_DISTANCE = var->get_float();
    }
  return NPC_ATTACK_FINISH_DISTANCE;
  }

bool FightAlgo::isEnemyPrehit(const Npc& npc, const Npc& tg, GameScript& owner) const {
  return tg.isPrehit() && isInWRange(tg,npc,owner) && isInFocusAngle(tg,npc) && isInFocusAngle(npc,tg);
  }

bool FightAlgo::isInAttackRange(const Npc &npc, const Npc &tg, GameScript &owner) const {
  auto dist = qDistTo(npc, tg);
  auto pd   = prefferedAttackDistance(npc,tg,owner);
  return (dist<=pd*pd);
  }

bool FightAlgo::isInFinishRange(const Npc& npc, const Npc& tg, GameScript& owner) const {
  auto dist = qDistTo(npc, tg);
  auto pd   = attackFinishDistance(owner);
  return (dist<=pd*pd);
  }

bool FightAlgo::isInCloseupRange(const Npc& npc, const Npc& tg, GameScript& owner) const {
  // script: automatic movement of the figure (if too close) to 0.75*FightRange
  auto dist = qDistTo(npc, tg);
  auto pd   = baseDistance(npc,tg,owner) * 0.75f;
  return (dist<=pd*pd);
  }

bool FightAlgo::isInWRange(const Npc& npc, const Npc& tg, GameScript& owner) const {
  // tested in vanilla on Bloofly's:
  //  60 weapon range (Spiked club) is not enough to hit
  //  70 weapon range (Rusty Sword) is good to hit
  static float padding = 0; // padding
  auto dist = qDistTo(npc, tg);
  auto pd   = prefferedAttackDistance(npc,tg,owner) + padding;
  return (dist<=pd*pd);
  }

bool FightAlgo::isInGRange(const Npc &npc, const Npc &tg, GameScript &owner) const {
  auto dist = qDistTo(npc, tg);
  auto pd   = prefferedGDistance(npc,tg,owner);
  return (dist<=pd*pd);
  }

bool FightAlgo::isInFocusAngle(const Npc &npc, const Npc &tg) const {
  static const float maxAngle = std::cos(float(30.0*M_PI/180.0));
  return angleTest(npc, tg, maxAngle);
  }

bool FightAlgo::isInFocusAngle(const Npc& npc, const Npc& tg, float ang) const {
  const float maxAngle = std::cos(float(ang*M_PI/180.0));
  return angleTest(npc, tg, maxAngle);
  }

bool FightAlgo::isTargetLost(const Npc& npc, const Npc& tg, GameScript& owner) const {
  // own hit knocks the target back up to ~1.5 of weapon range, that is not running away;
  // after a block, a jump back or a miss weapon range applies
  const bool inRange = hitLanded ? isInGRange(npc,tg,owner) : isInWRange(npc,tg,owner);
  return !(inRange && isInFocusAngle(npc,tg));
  }

bool FightAlgo::isInJumpBackAngle(const Npc& npc, const Npc& tg) const {
  static const float maxAngle = std::cos(float(90.0*M_PI/180.0));
  return angleTest(npc, tg, maxAngle);
  }

bool FightAlgo::angleTest(const Npc& npc, const Npc& tg, float cosMax) {
  // must be consistent with collisions
  const auto  dpos = tg.collosionCenter() - npc.collosionCenter();
  const float plAng = npc.rotationRad();

  const float da = plAng-std::atan2(dpos.z,dpos.x);
  const float c  = std::cos(da);

  if(c<cosMax)
    return false;
  return true;
  }

float FightAlgo::weaponRange(GameScript &owner, const Npc &npc) {
  /*
  NOTE: comments from G2 scripts:
    Bip01 bis BBox
    FAI_W = BASE + ItemRange (or Fist)
    FAI_G = BASE + ItemRange (or Fist) + G
  */
  auto  gl  = npc.guild();
  auto& gv  = owner.guildVal();
  auto  w   = npc.inventory().activeWeapon();
  int   add = w ? w->swordLength() : 0;
  auto  bR  = Gothic::inst().version().game==2 ? ReferenceBowRangeG2 : ReferenceBowRangeG1;

  switch(npc.weaponState()) {
    case WeaponState::W1H:
      return float(gv.fight_range_1ha[gl] + add);
    case WeaponState::W2H:
      return float(gv.fight_range_2ha[gl] + add);
    case WeaponState::NoWeapon:
    case WeaponState::Fist:
      return float(gv.fight_range_fist[gl]);
    case WeaponState::Bow:
    case WeaponState::CBow:
      return float(bR);
    case WeaponState::Mage:
      return float(MaxMagRange);
    }
  return 0;
  }

