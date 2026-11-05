// ******************************************************************
// Melee practice of an npc (Gothic 2.5, spec 005)
// ------------------------------------------------------------------
// New file at the end of Gothic.src (decisions/0005).
// ******************************************************************

// ------ Engine functions of the OpenGothic fork (decisions/0010) ------
// An older engine ignores the calls and logs "not implemented call".

// Draws fists, also when a melee weapon is equipped.
extern func void AI_ReadyFist (var instance par0);

// One fight move without a target, which hurts nobody. Attacks link
// inside of the combo window of the previous practice attack; the talent
// limits the forward combo as in a fight. Move: PRACTICE_* below.
extern func void AI_PracticeMove (var instance par0, var int par1);

// ------ Moves of AI_PracticeMove ------
const int PRACTICE_FRONT    = 0;
const int PRACTICE_LEFT     = 1;
const int PRACTICE_RIGHT    = 2;
const int PRACTICE_BLOCK    = 3;
const int PRACTICE_JUMPBACK = 4;
