#pragma once

#include <cstdint>
#include <string_view>

#include "graphics/mesh/animationsolver.h"
#include "graphics/mesh/pose.h"
#include "game/constants.h"

class Npc;
class FightAlgo;

// Developer log of melee fights: one JSON object per line, written to the -results directory.
// Format: gothic25/tests/README.md. Available with -devmode only, off by default.
class FightLog final {
  public:
    static bool isEnabled() { return enabled; }
    static void setEnabled(bool e);

    static void attack(Npc& npc, AnimationSolver::Anim anim, BodyState bs, const Pose::ComboStart& cs,
                       uint16_t comboLen, const FightAlgo& fai);
    static void marker(std::string_view what, int32_t line = -1, std::string_view text = {}, std::string_view file = {});

  private:
    inline static bool enabled = false;
  };
