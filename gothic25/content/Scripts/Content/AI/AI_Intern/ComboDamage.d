// ******************************************************************
// Combo damage bonus (Gothic 2.5, spec 002)
// ------------------------------------------------------------------
// Read by the engine when present; without these constants every hit
// does the usual damage.
//
// Percent of the damage of a hit from a forward combo, applied after
// protection and the weak hit, before the minimal damage. Side attacks,
// run attacks, finishing moves, missiles and spells get no bonus.
//
// 1H and 2H tables: a row of 4 combo hits per talent level
// (novice, warrior, master). FIST tables: a single row.
// Hits beyond a row use its last value. The first hit stays at 100.
//
// NPC tables: half of the player's bonus above 100, rounded to 5.
//
// New file at the end of Gothic.src: new symbols elsewhere would shift
// the symbol numbers that saves refer to (decisions/0005).
// ******************************************************************

const int COMBO_DAMAGE_1H_PLAYER [12] =
{
//	hit 1	hit 2	hit 3	hit 4
	100,	130,	130,	130,	// novice
	100,	150,	200,	260,	// warrior
	100,	175,	275,	400		// master
};

const int COMBO_DAMAGE_2H_PLAYER [12] =
{
	100,	130,	130,	130,	// novice
	100,	150,	210,	210,	// warrior: combo of 3 hits
	100,	175,	275,	400		// master
};

const int COMBO_DAMAGE_FIST_PLAYER [4] =
{
	100,	150,	150,	150
};

const int COMBO_DAMAGE_1H_NPC [12] =
{
	100,	115,	115,	115,	// novice
	100,	125,	150,	180,	// warrior
	100,	140,	190,	250		// master
};

const int COMBO_DAMAGE_2H_NPC [12] =
{
	100,	115,	115,	115,	// novice
	100,	125,	155,	155,	// warrior: combo of 3 hits
	100,	140,	190,	250		// master
};

const int COMBO_DAMAGE_FIST_NPC [4] =
{
	100,	125,	125,	125
};
