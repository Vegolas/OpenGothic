#pragma once

#include <zenkit/DaedalusVm.hh>
#include <zenkit/addon/daedalus.hh>

class FightAi final {
  public:
    enum {
      // original scripts define MAX_MOVE = 6; mods may declare longer move lists
      MaxMoves = 16,
      };

    struct Moves final {
      zenkit::FightAiMove move[MaxMoves] = {};
      };

    // Optional combo settings of a tactic: FA_COMBO_<N> instance of C_FightAI_Combo.
    // Not present in original scripts; without it a tactic fights as before.
    struct Combo final {
      bool    enabled          = false; // link attacks inside the combo window
      int32_t link_min         = 0;     // link moment: percent of the usable combo window
      int32_t link_max         = 100;
      bool    defend_in_series = false; // may break own series to react on enemy_prehit
      bool    break_on_lost    = false; // breaks series, if enemy is out of range or focus
      };

    struct FA final {
      Moves enemy_prehit;      // Enemy attacks me
      Moves enemy_stormprehit; // Enemy makes a storm attack
      Moves my_w_combo;        // I'm in the combo window
      Moves my_w_runto;        // I run towards the opponent
      Moves my_w_strafe;       // Just take hit
      Moves my_w_focus;        // I have opponent in focus (can hit)
      Moves my_w_nofocus;      // I don't have opponent in focus

      // 'G' - range
      Moves my_g_combo;        // I'm in the combo window (not used in G2)
      Moves my_g_runto;        // I run towards the opponent (can make a storm attack)
      Moves my_g_strafe;       // not used in G2
      Moves my_g_focus;        // I have opponent in focus (can hit)

      // FK Range Foes (far away)
      Moves my_fk_focus;       // I have opponents in focus

      Moves my_g_fk_nofocus;   // I am NOT in focus of opponents (also applies to G-distance!)

      // Range + Magic  (used at each removal)
      Moves my_fk_focus_far;   // Opponents in focus
      Moves my_fk_nofocus_far; // Opponents NOT in focus

      Moves my_fk_focus_mag;   // Opponents in focus
      Moves my_fk_nofocus_mag; // Opponents NOT in focus

      Combo combo;
      };

    FightAi();

    const FA& operator[](size_t i) const;

  private:
    auto loadAi(zenkit::DaedalusVm &vm, std::string_view name) -> Moves;
    auto loadCombo(zenkit::DaedalusVm &vm, std::string_view name) -> Combo;
    FA   loadAi(zenkit::DaedalusVm &vm, size_t id);

    std::vector<FA> fAi;
  };
