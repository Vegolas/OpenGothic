// *******************************
// Kampf AI Klasse und Konstanten
// *******************************

// Reaktionen von NSCs können sein :
CONST INT	MOVE_RUN			= 1;	// Gegner in meinem Fokus + steht wer dazwischen? (G)
CONST INT	MOVE_RUNBACK		= 2; 	// Gegner in meinem Fokus
CONST INT	MOVE_JUMPBACK		= 3;
CONST INT	MOVE_TURN			= 4;	// Immer bis Gegner im Fokus (also nie durch neue Aktion unterbrochen, höchstens durch Gegner-Attacke)
CONST INT	MOVE_STRAFE			= 5; 	// (Richtung wird vom Programm entschieden)
CONST INT 	MOVE_ATTACK			= 6;	// in ComboZone = Combo / im Rennen = Sturmattacke?
const INT 	MOVE_SIDEATTACK		= 7;
CONST INT 	MOVE_FRONTATTACK	= 8;
CONST INT 	MOVE_TRIPLEATTACK	= 9;
CONST INT 	MOVE_WHIRLATTACK	= 10;
CONST INT 	MOVE_MASTERATTACK	= 11;
CONST INT 	MOVE_TURNTOHIT		= 15;	// Version > 0.92 => No Effect 
CONST INT	MOVE_PARADE			= 17;	// (keine Attacke = oben)
CONST INT	MOVE_STANDUP		= 18;
CONST INT 	MOVE_WAIT			= 19;
CONST INT	MOVE_WAIT_LONGER	= 23;		// Achtung: Muss 23 sein, da im Programm noch einige unbenutze Moves zwischen 19 und 22 gibt
CONST INT	MOVE_WAIT_EXT		= 24;		// Achtung: Muss 24 sein, da im Programm noch einige unbenutze Moves zwischen 19 und 22 gibt

CONST INT	MAX_MOVE			= 12;	// FightMove-Variationen pro FAI-Funktion (Gothic 2.5: the original engine reads 6, OpenGothic up to 16)

CONST INT 	MAX_FIGHTAI			= 50;	// Anzahl vorhandener Fight-AIs //Konstante NICHT redundant im Programmcode, kann hier beliebig verändert werden


// ******
// Klasse
// ******

CLASS C_FightAI 
{
	VAR INT move[MAX_MOVE];
};

// Gothic 2.5: optional per-tactic combo settings, read by OpenGothic from FA_COMBO_<N>.
// A fight tactic without such an instance fights like in the original game.
CLASS C_FightAI_Combo
{
	VAR INT link_min;			// earliest moment to link the next attack, percent of the usable combo window
	VAR INT link_max;			// latest moment to link the next attack, percent of the usable combo window
	VAR INT defend_in_series;	// TRUE: may break an own series to react to an enemy attack (FA_ENEMY_PREHIT_<N>)
	VAR INT break_on_lost;		// TRUE: breaks a series when the enemy leaves weapon range or focus
};

