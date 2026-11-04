#pragma once

#include <cstdint>
#include <zenkit/addon/daedalus.hh>
#include <Tempest/Vec>

#include "game/definitions/fightaidefinitions.h"

class Npc;
class GameScript;
class Serialize;

class FightAlgo final {
  public:
    FightAlgo();

    void load(Serialize& fin);
    void save(Serialize& fout);

    enum Action : uint8_t {
      MV_NULL     = 0,
      MV_MOVEG    = 1,
      MV_MOVE     = 2,
      MV_JUMPBACK = 3,
      MV_ATTACK   = 4,
      MV_ATTACKL  = 5,
      MV_ATTACKR  = 6,
      MV_STRAFEL  = 7,
      MV_STRAFER  = 8,
      MV_BLOCK    = 9,
      MV_WAIT     = 10,
      MV_WAITLONG = 11,
      MV_TURN2HIT = 12,
      MV_TURN     = 13,
      MV_TURNG    = 14,
      MV_STRAFE_E = 15,

      MV_MAX      = 6
      };

    // attack series of the last expanded FAI move, for the fight log; not serialized
    struct Series final {
      zenkit::FightAiMove move = zenkit::FightAiMove::NOP;
      uint32_t            id   = 0; // counts series of this npc
      uint8_t             len  = 0; // attacks in the move
      uint8_t             done = 0; // attacks of the move consumed so far
      };

    Action nextFromQueue(Npc &npc, Npc &tg, GameScript& owner);
    void   consumeAction();
    void   dropForwardAttacks(bool leftForward, bool rightForward);
    void   onClearTarget();
    void   onTakeHit();
    void   onBreakSeries();
    void   onHitFrame();
    void   onHitLanded();
    bool   onEnemyPrehit(Npc &npc, Npc &tg, GameScript& owner);

    bool   hasInstructions() const;
    auto   series() const -> const Series& { return ser; }
    bool   isHitLanded() const { return hitLanded; }
    bool   isInSeries() const { return ser.len>0 && hasInstructions(); }
    bool   fetchInstructions(Npc &npc, Npc &tg, GameScript& owner);
    float  qDistTo(const Npc& npc, const Npc& tg) const;

    bool     hasCombo     (Npc &npc) const;
    auto     comboAi      (Npc &npc) const -> const FightAi::Combo&;
    uint64_t comboLinkTime(Npc &npc, uint64_t winBegin, uint64_t winEnd, GameScript &owner);
    bool     comboContinue(Npc &npc, uint64_t winBegin, GameScript &owner);

    float  baseDistance           (const Npc &npc, const Npc &tg, GameScript &owner) const;
    float  prefferedAttackDistance(const Npc &npc, const Npc &tg, GameScript &owner) const;
    float  prefferedGDistance     (const Npc &npc, const Npc &tg, GameScript &owner) const;
    float  attackFinishDistance   (GameScript &owner) const;

    bool   isEnemyPrehit          (const Npc &npc, const Npc &tg, GameScript &owner) const;
    bool   isInAttackRange        (const Npc &npc, const Npc &tg, GameScript &owner) const;
    bool   isInFinishRange        (const Npc &npc, const Npc &tg, GameScript &owner) const;
    bool   isInCloseupRange       (const Npc &npc, const Npc &tg, GameScript &owner) const;
    bool   isInWRange             (const Npc &npc, const Npc &tg, GameScript &owner) const;
    bool   isInGRange             (const Npc &npc, const Npc &tg, GameScript &owner) const;
    bool   isInFocusAngle         (const Npc &npc, const Npc &tg) const;
    bool   isInFocusAngle         (const Npc &npc, const Npc &tg, float ang) const;
    bool   isInJumpBackAngle      (const Npc &npc, const Npc &tg) const;
    bool   isTargetLost           (const Npc &npc, const Npc &tg, GameScript &owner) const;

  private:
    void   fillQueue(Npc &npc, Npc &tg, GameScript& owner);
    bool   fillQueue(GameScript& owner, const FightAi::Moves& src);
    void   startSeries(zenkit::FightAiMove mv);

    static zenkit::FightAiMove randomMove(GameScript& owner, const FightAi::Moves& src);
    static bool   angleTest(const Npc& npc, const Npc& tg, float cosMax);
    static float  weaponRange(GameScript &owner,const Npc &npc);

    zenkit::FightAiMove queueId = zenkit::FightAiMove::NOP;
    Action              tr   [MV_MAX]={};
    bool                hitFlg=false;

    // combo link moment and combo continuation, rolled once per combo window; not serialized
    uint64_t            linkWindow = 0;
    uint64_t            linkTime   = 0;
    uint64_t            contWindow = 0;
    bool                contAttack = false;
    Series              ser;
    // last attack hit the target and knocked it back; not serialized
    bool                hitLanded  = false;
  };
