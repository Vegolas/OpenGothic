#pragma once

#include <cstdint>
#include <string>
#include <string_view>
#include <vector>

#include "game/fightlog.h"
#include "marvin.h"

// Test scenario: console commands from a file, executed once the world is loaded.
// Started by -scenario <file>, -devmode only. Format: gothic25/tests/README.md
class ScenarioRunner final {
  public:
    ScenarioRunner();
    ~ScenarioRunner();

    void onWorldLoaded();
    void tick();

  private:
    enum Kind : uint8_t {
      K_Console,
      K_Wait,
      K_WaitEvent,
      K_Quit,
      };

    enum EventKind : uint8_t {
      E_Series,
      E_SeriesHit,
      E_Combo,
      E_Down,
      E_Unconscious,
      E_Dead,
      };

    enum State : uint8_t {
      S_Idle,
      S_Running,
      S_Done,
      };

    struct Line final {
      int32_t     num    = 0;
      Kind        kind   = K_Console;
      uint64_t    waitMs = 0; // wait time, or the time limit of an event wait
      EventKind   event  = E_Series;
      int32_t     n      = 0;
      std::string who;
      std::string text;
      };

    struct EventWait final {
      const Line* line     = nullptr;
      bool        hero     = false;
      size_t      instance = size_t(-1);
      uint64_t    deadline = 0;
      bool        done     = false;
      };

    void load(std::u16string_view file);
    void exec(const Line& l, uint64_t now);
    void finish(bool quit);
    void fail(int32_t line, std::string_view msg);
    void writeStatus(std::string_view result, int32_t line, std::string_view msg);
    void onPrint(std::string_view msg);
    void onFightEvent(const FightLog::Event& e);
    bool parseEventWait(Line& l, const std::vector<std::string_view>& args);

    Marvin            marvin;
    std::vector<Line> lines;
    size_t            pc        = 0;
    State             state     = S_Idle;
    bool              exitOnEnd = false;
    uint64_t          waitUntil = 0;
    EventWait         evWait;
    int32_t           saveLine  = -1;
    std::string       saveFile;
    std::string       lastPrint;
  };
