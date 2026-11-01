#pragma once

#include <Tempest/Signal>

#include <cstdint>
#include <string_view>

#include "graphics/mesh/animationsolver.h"
#include "graphics/mesh/pose.h"
#include "game/constants.h"
#include "game/fightalgo.h"

class Npc;

// Developer log of melee fights: one JSON object per line, written to the -results directory.
// Format: gothic25/tests/README.md. Available with -devmode only, off by default.
class FightLog final {
  public:
    // logged attack or state, for scenario waits
    struct Event final {
      Npc*             npc       = nullptr;
      std::string_view type;          // "attack" or "state"
      std::string_view state;         // state: stumble, fly, lie, unconscious, dead
      int32_t          combo     = 0; // attack: forward combo stage, from 1
      int32_t          seriesPos = 0; // attack from a FAI series: position and length; 0 otherwise
      int32_t          seriesLen = 0;
      };
    inline static Tempest::Signal<void(const Event&)> onEvent;

    static bool isEnabled() { return enabled; }
    static void setEnabled(bool e);

    static void attack(Npc& npc, AnimationSolver::Anim anim, BodyState bs, const Pose::ComboStart& cs,
                       uint16_t comboLen, const FightAlgo& fai);
    static void miss  (Npc& npc, Npc* tgt, std::string_view why, uint16_t comboLen);
    static void defend(Npc& npc, Npc& tgt, bool jumpBack, uint16_t comboLen);
    static void hit   (Npc& npc, Npc& tgt, uint16_t comboLen, int32_t dmg, int32_t bonus, int32_t hpBefore, bool stagger);
    static void state (Npc& npc, std::string_view st, Npc* by);
    static void seriesBreak(Npc& npc, const FightAlgo::Series& ser, bool queued, std::string_view why,
                            std::string_view detail = {});
    static void marker(std::string_view what, int32_t line = -1, std::string_view text = {}, std::string_view file = {});

  private:
    inline static bool enabled = false;
  };
