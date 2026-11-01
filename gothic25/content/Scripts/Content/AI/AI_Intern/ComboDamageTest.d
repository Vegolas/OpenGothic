// ******************************************************************
// Combo damage test target (Gothic 2.5, spec 002)
// ------------------------------------------------------------------
// A human without weapon and armor (protection 0) that stands still:
// all perceptions are off, so it never blocks, flees or strikes back.
// Test scenarios insert it (insert TST_ComboDummy) and read the damage
// of each hit from the fight log. It is not placed in the world.
//
// New file at the end of Gothic.src (decisions/0005).
// ******************************************************************

func void ZS_ComboDummy ()
{
	B_ClearPerceptions (self);
	AI_StandUp (self);
};

func int ZS_ComboDummy_Loop ()
{
	return LOOP_CONTINUE;
};

func void ZS_ComboDummy_End ()
{
};

instance TST_ComboDummy (Npc_Default)
{
	// ------ NSC ------
	name 		= "Cel testowy";
	guild 		= GIL_NONE;
	id 			= 9900;
	voice 		= 13;
	flags       = 0;
	npctype		= NPCTYPE_AMBIENT;

	// ------ Attribute ------
	level 							= 1;
	attribute[ATR_STRENGTH] 		= 10;
	attribute[ATR_DEXTERITY] 		= 10;
	attribute[ATR_HITPOINTS_MAX]	= 100000;
	attribute[ATR_HITPOINTS]		= 100000;

	// ------ Kampf-Taktik ------
	fight_tactic		= FAI_HUMAN_COWARD;

	// ------ visuals ------
	B_SetNpcVisual 		(self, MALE, "Hum_Head_FatBald", Face_N_Normal03, BodyTex_N, NO_ARMOR);

	// ------ AI ------
	start_aistate		= ZS_ComboDummy;
};
