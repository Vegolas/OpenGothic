// ******************************************************************
// Melee practice: test helpers (Gothic 2.5, spec 005)
// ------------------------------------------------------------------
// Functions and characters for the test scenarios of spec 005
// (tests/005, tests/dev), called with "call <function> <npc> ...".
// No npc of the world uses them.
//
// New file at the end of Gothic.src (decisions/0005).
// ******************************************************************

const int TST_WEAPON_1H = 1;
const int TST_WEAPON_2H = 2;

// Gives an inserted npc a paladin sword (TST_WEAPON_1H or _2H) and the
// fight talent in percent, see B_SetFightSkills.
func void TST_Arm (var C_NPC slf, var int weapon, var int percent)
{
	if (weapon == TST_WEAPON_2H)
	{
		EquipItem (slf, ItMw_2h_Pal_Sword);
	}
	else
	{
		EquipItem (slf, ItMw_1h_Pal_Sword);
	};
	B_SetFightSkills (slf, percent);
};

func void TST_ReadyMelee (var C_NPC slf)
{
	AI_ReadyMeleeWeapon (slf);
};

func void TST_ReadyFist (var C_NPC slf)
{
	AI_ReadyFist (slf);
};

func void TST_PracticeMove (var C_NPC slf, var int move)
{
	AI_PracticeMove (slf, move);
};

func int TST_IsFistMode (var C_NPC slf)
{
	return Npc_IsInFightMode (slf, FMODE_FIST);
};

func int TST_IsMeleeMode (var C_NPC slf)
{
	return Npc_IsInFightMode (slf, FMODE_MELEE);
};
