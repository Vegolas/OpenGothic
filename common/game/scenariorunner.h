#pragma once

#include <cstdint>
#include <string>
#include <string_view>
#include <vector>

#include "marvin.h"

// Test scenario: console commands from a file, executed once the world is loaded.
// Started by -scenario <file>, -devmode only. Format: gothic25/tests/README.md
class ScenarioRunner final {
  public:
    ScenarioRunner();

    void onWorldLoaded();
    void tick();

  private:
    enum Kind : uint8_t {
      K_Console,
      K_Wait,
      K_Quit,
      };

    enum State : uint8_t {
      S_Idle,
      S_Running,
      S_Done,
      };

    struct Line final {
      int32_t     num    = 0;
      Kind        kind   = K_Console;
      uint64_t    waitMs = 0;
      std::string text;
      };

    void load(std::u16string_view file);
    void exec(const Line& l, uint64_t now);
    void finish(bool quit);
    void fail(int32_t line, std::string_view msg);
    void writeStatus(std::string_view result, int32_t line, std::string_view msg);
    void onPrint(std::string_view msg);

    Marvin            marvin;
    std::vector<Line> lines;
    size_t            pc        = 0;
    State             state     = S_Idle;
    bool              exitOnEnd = false;
    uint64_t          waitUntil = 0;
    int32_t           saveLine  = -1;
    std::string       saveFile;
    std::string       lastPrint;
  };
