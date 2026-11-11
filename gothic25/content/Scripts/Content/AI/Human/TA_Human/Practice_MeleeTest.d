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

// Sets a target, like one left over from a fight (Z3).
func void TST_SetTarget (var C_NPC slf, var C_NPC oth)
{
	Npc_SetTarget (slf, oth);
};

func int TST_HasTarget (var C_NPC slf)
{
	return Npc_GetTarget (slf);
};

func int TST_HpLost (var C_NPC slf)
{
	return slf.attribute[ATR_HITPOINTS_MAX] - slf.attribute[ATR_HITPOINTS];
};

// hitpoints lost by three characters together (spec 005 K6)
func int TST_HpLostSum (var C_NPC a, var C_NPC b, var C_NPC c)
{
	return TST_HpLost (a) + TST_HpLost (b) + TST_HpLost (c);
};

// Sets the waypoint of the daily routine (self.wp), the place of the practice (Z4).
func void TST_SetWp (var C_NPC slf, var string wp)
{
	slf.wp = wp;
};

// Starts an ordinary ai state, for the "ai" event of the fight log (Z4).
func void TST_StartStand (var C_NPC slf)
{
	AI_StartState (slf, ZS_Stand_ArmsCrossed, 0, "");
};

// Starts the practice state without a daily routine (Z6), at the waypoint of slf (TST_SetWp).
func void TST_StartPractice (var C_NPC slf, var int fist)
{
	if (fist)
	{
		AI_StartState (slf, ZS_Practice_Fist, 1, "");
	}
	else
	{
		AI_StartState (slf, ZS_Practice_Melee, 1, "");
	};
};

func void TST_SetProfile (var C_NPC slf, var int profile)
{
	slf.aivar[AIV_PracticeProfile] = profile;
};

func void TST_SetWalk (var C_NPC slf)
{
	AI_SetWalkmode (slf, NPC_WALK);
};

func int TST_HasMeleeWeapon (var C_NPC slf)
{
	return Npc_HasEquippedMeleeWeapon (slf);
};

// the mace the old sword practice gives to npcs without a weapon (spec 005 K3)
func int TST_HasMace (var C_NPC slf)
{
	return Npc_HasItems (slf, ItMw_1h_Bau_Mace);
};

// B_RefreshAtInsert already gives an inserted militia npc without a weapon a mace in the
// inventory: K3 checks that the practice adds none, from the mark to the end.
var int TST_MaceMark;

func void TST_MarkMace (var C_NPC slf)
{
	TST_MaceMark = Npc_HasItems (slf, ItMw_1h_Bau_Mace);
};

func int TST_MaceGained (var C_NPC slf)
{
	return Npc_HasItems (slf, ItMw_1h_Bau_Mace) - TST_MaceMark;
};

func int TST_IsPracticing (var C_NPC slf)
{
	if (Npc_IsInState (slf, ZS_Practice_Melee))
	|| (Npc_IsInState (slf, ZS_Practice_Fist))
	{
		return TRUE;
	};
	return FALSE;
};

func int TST_IsWeaponless (var C_NPC slf)
{
	return Npc_IsInFightMode (slf, FMODE_NONE);
};

// at the place of a waypoint, within 3 m (spec 005 K8)
func int TST_IsNearWp (var C_NPC slf, var string wp)
{
	return Npc_GetDistToWP (slf, wp) < 300;
};

// the old sword practice of the game (spec 005 K11)
func int TST_IsOldPractice (var C_NPC slf)
{
	return Npc_IsInState (slf, ZS_Practice_Sword);
};

func int TST_IsFistMode (var C_NPC slf)
{
	return Npc_IsInFightMode (slf, FMODE_FIST);
};

func int TST_IsMeleeMode (var C_NPC slf)
{
	return Npc_IsInFightMode (slf, FMODE_MELEE);
};

// ------------------------------------------------------------------
// Characters of the practice scenarios (spec 005 Z7). They train at
// the yard of the city barracks; scenarios remove the militia 330 and
// 331, who practice at CENTRE_03 and CENTRE_04 from 7:00.
// ------------------------------------------------------------------

const string TST_PRACTICE_WP_1 = "NW_CITY_HABOUR_KASERN_CENTRE_01";
const string TST_PRACTICE_WP_3 = "NW_CITY_HABOUR_KASERN_CENTRE_03";
const string TST_PRACTICE_WP_4 = "NW_CITY_HABOUR_KASERN_CENTRE_04";

func void Rtn_Start_9910 ()
{
	TA_Practice_Melee	(00,00,12,00, TST_PRACTICE_WP_1);
	TA_Practice_Melee	(12,00,00,00, TST_PRACTICE_WP_1);
};

func void Rtn_Start_9911 ()
{
	TA_Practice_Melee	(00,00,12,00, TST_PRACTICE_WP_3);
	TA_Practice_Melee	(12,00,00,00, TST_PRACTICE_WP_3);
};

func void Rtn_Start_9912 ()
{
	TA_Practice_Melee	(00,00,12,00, TST_PRACTICE_WP_4);
	TA_Practice_Melee	(12,00,00,00, TST_PRACTICE_WP_4);
};

func void Rtn_Start_9913 ()
{
	TA_Practice_Fist	(00,00,12,00, TST_PRACTICE_WP_1);
	TA_Practice_Fist	(12,00,00,00, TST_PRACTICE_WP_1);
};

func void Rtn_Start_9914 ()
{
	TA_Practice_Melee	(00,00,12,00, TST_PRACTICE_WP_3);
	TA_Practice_Melee	(12,00,00,00, TST_PRACTICE_WP_3);
};

func void Rtn_Start_9915 ()
{
	TA_Practice_Melee	(00,00,12,00, TST_PRACTICE_WP_4);
	TA_Practice_Melee	(12,00,00,00, TST_PRACTICE_WP_4);
};

// spec 005 K8: practice from 8:00 to 9:00, then standing at another place
func void Rtn_Start_9916 ()
{
	TA_Practice_Melee		(08,00,09,00, TST_PRACTICE_WP_1);
	TA_Stand_ArmsCrossed	(09,00,08,00, TST_PRACTICE_WP_3);
};

// militia 329 practices the new way at its own place, for its dialogs (spec 005 K7)
func void Rtn_TST_Practice_329 ()
{
	TA_Practice_Melee	(00,00,12,00, "NW_CITY_HABOUR_KASERN_CENTRE_02");
	TA_Practice_Melee	(12,00,00,00, "NW_CITY_HABOUR_KASERN_CENTRE_02");
};

// B_StartOtherRoutine also ends the current state (AI_ContinueRoutine): Npc_ExchangeRoutine alone
// keeps the old practice until the end of its time.
func void TST_PracticeMilitia ()
{
	var C_NPC mil;
	mil = Hlp_GetNpc (Mil_329_Miliz);
	B_StartOtherRoutine (mil, "TST_Practice");
};

// 1H master (K1, K5, K6, K10)
instance TST_Practice_Master1H (Npc_Default)
{
	name 		= "Ćwiczący mistrz 1H";
	guild 		= GIL_MIL;
	id 			= 9910;
	voice 		= 6;
	flags       = 0;
	npctype		= NPCTYPE_AMBIENT;
	B_SetAttributesToChapter (self, 3);
	fight_tactic		= FAI_HUMAN_MASTER;
	EquipItem			(self, ItMw_1h_Pal_Sword);
	B_SetNpcVisual 		(self, MALE, "Hum_Head_Bald", Face_N_NormalBart10, BodyTex_N, ITAR_MIL_L);
	B_SetFightSkills 	(self, 80);
	daily_routine 		= Rtn_Start_9910;
};

// 2H novice and 2H master side by side (K2)
instance TST_Practice_Novice2H (Npc_Default)
{
	name 		= "Ćwiczący nowicjusz 2H";
	guild 		= GIL_MIL;
	id 			= 9911;
	voice 		= 6;
	flags       = 0;
	npctype		= NPCTYPE_AMBIENT;
	B_SetAttributesToChapter (self, 3);
	fight_tactic		= FAI_HUMAN_COWARD;
	EquipItem			(self, ItMw_2h_Pal_Sword);
	B_SetNpcVisual 		(self, MALE, "Hum_Head_Fighter", Face_N_Normal03, BodyTex_N, ITAR_MIL_L);
	B_SetFightSkills 	(self, 20);
	daily_routine 		= Rtn_Start_9911;
};

instance TST_Practice_Master2H (Npc_Default)
{
	name 		= "Ćwiczący mistrz 2H";
	guild 		= GIL_MIL;
	id 			= 9912;
	voice 		= 6;
	flags       = 0;
	npctype		= NPCTYPE_AMBIENT;
	B_SetAttributesToChapter (self, 3);
	fight_tactic		= FAI_HUMAN_MASTER;
	EquipItem			(self, ItMw_2h_Pal_Sword);
	B_SetNpcVisual 		(self, MALE, "Hum_Head_Pony", Face_N_Normal03, BodyTex_N, ITAR_MIL_L);
	B_SetFightSkills 	(self, 80);
	daily_routine 		= Rtn_Start_9912;
};

// fists with a 1H sword equipped (K3)
instance TST_Practice_Fist1H (Npc_Default)
{
	name 		= "Ćwiczący pięściami";
	guild 		= GIL_MIL;
	id 			= 9913;
	voice 		= 6;
	flags       = 0;
	npctype		= NPCTYPE_AMBIENT;
	B_SetAttributesToChapter (self, 3);
	fight_tactic		= FAI_HUMAN_STRONG;
	EquipItem			(self, ItMw_1h_Pal_Sword);
	B_SetNpcVisual 		(self, MALE, "Hum_Head_Bald", Face_N_Normal03, BodyTex_N, ITAR_MIL_L);
	B_SetFightSkills 	(self, 80);
	daily_routine 		= Rtn_Start_9913;
};

// no melee weapon, practice with the weapon: fists (K3)
instance TST_Practice_NoWeapon (Npc_Default)
{
	name 		= "Ćwiczący bez broni";
	guild 		= GIL_MIL;
	id 			= 9914;
	voice 		= 6;
	flags       = 0;
	npctype		= NPCTYPE_AMBIENT;
	B_SetAttributesToChapter (self, 3);
	fight_tactic		= FAI_HUMAN_STRONG;
	B_SetNpcVisual 		(self, MALE, "Hum_Head_Fighter", Face_N_NormalBart10, BodyTex_N, ITAR_MIL_L);
	B_SetFightSkills 	(self, 40);
	daily_routine 		= Rtn_Start_9914;
};

// test profile 99: attacks from the left only, a pause of 2 s (K4)
instance TST_Practice_Profile (Npc_Default)
{
	name 		= "Ćwiczący profil testowy";
	guild 		= GIL_MIL;
	id 			= 9915;
	voice 		= 6;
	flags       = 0;
	npctype		= NPCTYPE_AMBIENT;
	B_SetAttributesToChapter (self, 3);
	fight_tactic		= FAI_HUMAN_STRONG;
	EquipItem			(self, ItMw_1h_Pal_Sword);
	B_SetNpcVisual 		(self, MALE, "Hum_Head_Pony", Face_N_NormalBart10, BodyTex_N, ITAR_MIL_L);
	B_SetFightSkills 	(self, 80);
	aivar[AIV_PracticeProfile] = PRACTICE_PROFILE_TEST;
	daily_routine 		= Rtn_Start_9915;
};

// practice until 9:00, then standing at CENTRE_03 (K8)
instance TST_Practice_Shift (Npc_Default)
{
	name 		= "Ćwiczący do 9:00";
	guild 		= GIL_MIL;
	id 			= 9916;
	voice 		= 6;
	flags       = 0;
	npctype		= NPCTYPE_AMBIENT;
	B_SetAttributesToChapter (self, 3);
	fight_tactic		= FAI_HUMAN_STRONG;
	EquipItem			(self, ItMw_1h_Pal_Sword);
	B_SetNpcVisual 		(self, MALE, "Hum_Head_Bald", Face_N_Normal03, BodyTex_N, ITAR_MIL_L);
	B_SetFightSkills 	(self, 80);
	daily_routine 		= Rtn_Start_9916;
};

// ------------------------------------------------------------------
// Bystander of spec 005 K6: a citizen that stands where it was
// inserted, with the normal perceptions of humans, so it reacts to a
// fight, a threat or damage as any citizen would.
// ------------------------------------------------------------------

func void ZS_TST_Bystander ()
{
	Perception_Set_Normal ();
	B_ResetAll (self);
	AI_StandUp (self);
};

func int ZS_TST_Bystander_Loop ()
{
	return LOOP_CONTINUE;
};

func void ZS_TST_Bystander_End ()
{
};

instance TST_Practice_Bystander (Npc_Default)
{
	name 		= "Gapiący się mieszczanin";
	guild 		= GIL_VLK;
	id 			= 9917;
	voice 		= 1;
	flags       = 0;
	npctype		= NPCTYPE_AMBIENT;
	B_SetAttributesToChapter (self, 1);
	fight_tactic		= FAI_HUMAN_COWARD;
	B_SetNpcVisual 		(self, MALE, "Hum_Head_FatBald", Face_N_Normal03, BodyTex_N, ITAR_Vlk_L);
	start_aistate		= ZS_TST_Bystander;
};

// still in its own state: no fight, no flight, no reaction (spec 005 K6)
func int TST_IsCalm (var C_NPC slf)
{
	return Npc_IsInState (slf, ZS_TST_Bystander);
};

func int TST_IsMonsterCalm (var C_NPC slf)
{
	if (Npc_IsInState (slf, ZS_MM_Attack))
	|| (Npc_IsInState (slf, ZS_MM_Flee))
	{
		return FALSE;
	};
	return TRUE;
};
