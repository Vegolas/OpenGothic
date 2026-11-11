// ******************************************************************
// Melee practice of an npc (Gothic 2.5, spec 005)
// ------------------------------------------------------------------
// Daily routines:
//   TA_Practice_Melee - the npc practices with its melee weapon, with
//                       fists when it has none; it gets no weapon
//   TA_Practice_Fist  - the npc practices with fists, also when it
//                       has a weapon
// Each loop of the state is one series: now and then a block or a
// jump-back, attacks of a random kind, back to the waypoint, then a
// pause and now and then a longer rest. The engine plays the moves
// without a target and without damage (AI_PracticeMove); the talent
// of the npc limits its forward combo as in a fight.
//
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

// ------ Aivars of the practice ------
const int AIV_PracticeProfile	= 90;	// profile of the settings below, 0 - default; set it in the npc instance
const int AIV_PracticeDefend	= 91;	// series left until the next block or jump-back
const int AIV_PracticeRest		= 92;	// series left until the next rest

// ------ Settings (spec 005 W4) ------
// B_PracticeMelee_Settings sets them for self before every series:
// profile 0 first (spec 005 W2, W3), then the profile of the npc.
const int PRACTICE_PROFILE_TEST = 99;	// test profile of spec 005 K4, no npc of the world uses it

var int PracticeMelee_Fwd;				// weights of the series kinds: one forward attack,
var int PracticeMelee_Combo;			// forward combo,
var int PracticeMelee_Left;				// one attack from the left,
var int PracticeMelee_Right;			// one attack from the right,
var int PracticeMelee_Mixed;			// mixed series
var int PracticeMelee_ComboMax;			// longest forward combo ordered, 2-4; the talent cuts it shorter
var int PracticeMelee_MixedMax;			// longest mixed series, 2-3
var int PracticeMelee_DefendMin;		// a block or a jump-back every DefendMin-DefendMax series, 0 - never
var int PracticeMelee_DefendMax;
var int PracticeMelee_PauseMin;			// pause after a series, ms, for the talent level of the npc
var int PracticeMelee_PauseMax;
var int PracticeMelee_RestEveryMin;		// a rest instead of the pause every RestEveryMin-RestEveryMax series, 0 - never
var int PracticeMelee_RestEveryMax;
var int PracticeMelee_RestMin;			// rest, ms
var int PracticeMelee_RestMax;

func int B_PracticeMelee_Random (var int lo, var int hi)
{
	if (hi <= lo)
	{
		return lo;
	};
	return lo + Hlp_Random (hi - lo + 1);
};

// level: talent level of the weapon the npc practices with (0 novice, 1 warrior, 2 master)
func void B_PracticeMelee_Settings (var int level)
{
	// ------ Profile 0: spec 005 W2, W3 ------
	PracticeMelee_Fwd			= 20;
	PracticeMelee_Combo			= 30;
	PracticeMelee_Left			= 15;
	PracticeMelee_Right			= 15;
	PracticeMelee_Mixed			= 20;
	PracticeMelee_ComboMax		= 4;
	PracticeMelee_MixedMax		= 3;
	PracticeMelee_DefendMin		= 3;
	PracticeMelee_DefendMax		= 7;
	PracticeMelee_RestEveryMin	= 4;
	PracticeMelee_RestEveryMax	= 8;
	PracticeMelee_RestMin		= 6000;
	PracticeMelee_RestMax		= 10000;

	if (level >= 2)
	{
		PracticeMelee_PauseMin	= 500;
		PracticeMelee_PauseMax	= 2000;
	}
	else if (level == 1)
	{
		PracticeMelee_PauseMin	= 1000;
		PracticeMelee_PauseMax	= 3500;
	}
	else
	{
		PracticeMelee_PauseMin	= 2000;
		PracticeMelee_PauseMax	= 5000;
	};

	// ------ Profiles of the npcs ------
	if (self.aivar[AIV_PracticeProfile] == PRACTICE_PROFILE_TEST)
	{
		// spec 005 K4: attacks from the left only, a fixed pause of 2 s
		PracticeMelee_Fwd			= 0;
		PracticeMelee_Combo			= 0;
		PracticeMelee_Left			= 1;
		PracticeMelee_Right			= 0;
		PracticeMelee_Mixed			= 0;
		PracticeMelee_DefendMin		= 0;
		PracticeMelee_RestEveryMin	= 0;
		PracticeMelee_PauseMin		= 2000;
		PracticeMelee_PauseMax		= 2000;
	};
};

// Talent level of the practice: fists have no talent and count as a warrior (spec 005 W3).
func int B_PracticeMelee_Level (var int fist)
{
	if (fist)
	|| (!Npc_HasEquippedMeleeWeapon (self))
	{
		return 1;
	};
	var C_Item weapon;
	weapon = Npc_GetEquippedMeleeWeapon (self);
	if (weapon.flags & (ITEM_2HD_SWD | ITEM_2HD_AXE))
	{
		return Npc_GetTalentSkill (self, NPC_TALENT_2H);
	};
	return Npc_GetTalentSkill (self, NPC_TALENT_1H);
};

// Forward combo of 2 to ComboMax attacks; the engine drops what the talent does not allow.
func void B_PracticeMelee_Combo ()
{
	var int len;
	len = B_PracticeMelee_Random (2, PracticeMelee_ComboMax);
	AI_PracticeMove (self, PRACTICE_FRONT);
	AI_PracticeMove (self, PRACTICE_FRONT);
	if (len >= 3)
	{
		AI_PracticeMove (self, PRACTICE_FRONT);
	};
	if (len >= 4)
	{
		AI_PracticeMove (self, PRACTICE_FRONT);
	};
};

// Mixed series of 2 to MixedMax attacks: each attack differs from the one before, so the series
// always has a side attack.
func void B_PracticeMelee_Mixed ()
{
	var int len;
	var int move;
	len  = B_PracticeMelee_Random (2, PracticeMelee_MixedMax);
	move = Hlp_Random (3);
	AI_PracticeMove (self, move);
	move = (move + 1 + Hlp_Random (2)) % 3;
	AI_PracticeMove (self, move);
	if (len >= 3)
	{
		move = (move + 1 + Hlp_Random (2)) % 3;
		AI_PracticeMove (self, move);
	};
};

func void B_PracticeMelee_Series ()
{
	var int total;
	var int r;
	total = PracticeMelee_Fwd + PracticeMelee_Combo + PracticeMelee_Left + PracticeMelee_Right + PracticeMelee_Mixed;
	if (total <= 0)
	{
		AI_PracticeMove (self, PRACTICE_FRONT);
		return;
	};
	r = Hlp_Random (total);
	if (r < PracticeMelee_Fwd)
	{
		AI_PracticeMove (self, PRACTICE_FRONT);
		return;
	};
	r = r - PracticeMelee_Fwd;
	if (r < PracticeMelee_Combo)
	{
		B_PracticeMelee_Combo ();
		return;
	};
	r = r - PracticeMelee_Combo;
	if (r < PracticeMelee_Left)
	{
		AI_PracticeMove (self, PRACTICE_LEFT);
		return;
	};
	r = r - PracticeMelee_Left;
	if (r < PracticeMelee_Right)
	{
		AI_PracticeMove (self, PRACTICE_RIGHT);
		return;
	};
	B_PracticeMelee_Mixed ();
};

// Back to the place and its direction (spec 005 W5). AI_GotoWP stops up to about 60 cm from the
// waypoint; it also attaches the npc to the waypoint, which AI_AlignToWP needs, even when the npc
// is close. A second AI_GotoWP to the same waypoint does nothing.
func void B_PracticeMelee_Place ()
{
	AI_GotoWP (self, self.wp);
	AI_AlignToWP (self);
};

// A block or a jump-back before every DefendMin-DefendMax series (spec 005 W2). A jump-back, and
// a block with fists, move the npc: it goes back to its place before the series (spec 005 W5).
func void B_PracticeMelee_Defend ()
{
	if (PracticeMelee_DefendMin <= 0)
	{
		return;
	};
	if (self.aivar[AIV_PracticeDefend] > 0)
	{
		self.aivar[AIV_PracticeDefend] = self.aivar[AIV_PracticeDefend] - 1;
		return;
	};
	self.aivar[AIV_PracticeDefend] = B_PracticeMelee_Random (PracticeMelee_DefendMin, PracticeMelee_DefendMax) - 1;
	AI_PracticeMove (self, PRACTICE_BLOCK + Hlp_Random (2));
	B_PracticeMelee_Place ();
};

// Pause after a series, a rest every RestEveryMin-RestEveryMax series (spec 005 W3).
func void B_PracticeMelee_Pause ()
{
	if (PracticeMelee_RestEveryMin > 0)
	{
		if (self.aivar[AIV_PracticeRest] <= 0)
		{
			self.aivar[AIV_PracticeRest] = B_PracticeMelee_Random (PracticeMelee_RestEveryMin, PracticeMelee_RestEveryMax) - 1;
			AI_WaitMs (self, B_PracticeMelee_Random (PracticeMelee_RestMin, PracticeMelee_RestMax));
			return;
		};
		self.aivar[AIV_PracticeRest] = self.aivar[AIV_PracticeRest] - 1;
	};
	AI_WaitMs (self, B_PracticeMelee_Random (PracticeMelee_PauseMin, PracticeMelee_PauseMax));
};

func void B_PracticeMelee_Start (var int fist)
{
	Perception_Set_Normal ();
	B_ResetAll (self);
	AI_SetWalkmode (self, NPC_WALK);
	B_PracticeMelee_Place ();
	self.aivar[AIV_TAPOSITION] = NOTINPOS;

	B_PracticeMelee_Settings (B_PracticeMelee_Level (fist));
	self.aivar[AIV_PracticeDefend] = B_PracticeMelee_Random (PracticeMelee_DefendMin, PracticeMelee_DefendMax);
	self.aivar[AIV_PracticeRest]   = B_PracticeMelee_Random (PracticeMelee_RestEveryMin, PracticeMelee_RestEveryMax);

	// npcs that start together do not practice in one rhythm (spec 005 W3)
	AI_WaitMs (self, Hlp_Random (2000));
};

func void B_PracticeMelee_Loop (var int fist)
{
	if (self.aivar[AIV_TAPOSITION] == NOTINPOS)
	{
		if (fist)
		{
			AI_ReadyFist (self);
		}
		else
		{
			AI_ReadyMeleeWeapon (self);		// fists without a melee weapon
		};
		// the npc may come from far away: once more at the place before the first series
		B_PracticeMelee_Place ();
		self.aivar[AIV_TAPOSITION] = ISINPOS;
	};

	B_PracticeMelee_Settings (B_PracticeMelee_Level (fist));
	B_PracticeMelee_Defend ();
	B_PracticeMelee_Series ();

	// back to the place after every series (spec 005 W5)
	B_PracticeMelee_Place ();
	B_PracticeMelee_Pause ();
};

func void B_PracticeMelee_End ()
{
	AI_StandUp (self);
	AI_RemoveWeapon (self);
};

// ------ States ------
func void ZS_Practice_Melee ()
{
	B_PracticeMelee_Start (FALSE);
};

func int ZS_Practice_Melee_Loop ()
{
	B_PracticeMelee_Loop (FALSE);
	return LOOP_CONTINUE;
};

func void ZS_Practice_Melee_End ()
{
	B_PracticeMelee_End ();
};

func void ZS_Practice_Fist ()
{
	B_PracticeMelee_Start (TRUE);
};

func int ZS_Practice_Fist_Loop ()
{
	B_PracticeMelee_Loop (TRUE);
	return LOOP_CONTINUE;
};

func void ZS_Practice_Fist_End ()
{
	B_PracticeMelee_End ();
};

// ------ Daily routines ------
func void TA_Practice_Melee	(var int start_h, var int start_m, var int stop_h, var int stop_m, var string waypoint)	{TA_Min (self, start_h, start_m, stop_h, stop_m, ZS_Practice_Melee, waypoint);};
func void TA_Practice_Fist	(var int start_h, var int start_m, var int stop_h, var int stop_m, var string waypoint)	{TA_Min (self, start_h, start_m, stop_h, stop_m, ZS_Practice_Fist, waypoint);};
