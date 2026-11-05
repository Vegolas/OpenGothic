// ******************************************************************
// Melee practice of an npc (Gothic 2.5, spec 005)
// ------------------------------------------------------------------
// New file at the end of Gothic.src (decisions/0005).
// ******************************************************************

// ------ Engine functions of the OpenGothic fork (decisions/0010) ------
// An older engine ignores the calls and logs "not implemented call".

// Draws fists, also when a melee weapon is equipped.
extern func void AI_ReadyFist (var instance par0);
