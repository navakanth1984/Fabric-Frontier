export type Player = 'T' | 'G';
export type BoardPosition = string | null; // 'T', 'G', or null

export interface GameState {
  board: BoardPosition[];
  goatsToPlace: number;
  goatsCaptured: number;
  turn: Player;
  gameOver: boolean;
  winner: string | null;
}

export const ADJACENCY: Record<number, number[]> = {
  0: [1, 2],
  1: [0, 2, 3, 4],
  2: [0, 1, 4, 5],
  3: [1, 4, 6, 7],
  4: [1, 2, 3, 5, 7, 8],
  5: [2, 4, 8, 9],
  6: [3, 7, 10, 11],
  7: [3, 4, 6, 8, 11, 12],
  8: [4, 5, 7, 9, 12, 13],
  9: [5, 8, 13, 14],
  10: [6, 11, 15],
  11: [6, 7, 12, 16],
  12: [7, 8, 11, 13, 16, 17],
  13: [8, 9, 12, 14, 17, 18],
  14: [9, 13, 18],
  15: [10],
  16: [11, 12, 17, 19],
  17: [12, 13, 16, 18, 19, 20],
  18: [13, 14, 17, 20, 21],
  19: [16, 17, 20],
  20: [17, 18, 19, 21],
  21: [18, 20, 22],
  22: [21]
};

export const LINEAR_JUMPS: [number, number, number][] = [
  [0, 1, 3], [0, 2, 5], [1, 4, 8], [2, 4, 7],
  [3, 4, 5], [6, 7, 8], [7, 8, 9], [11, 12, 13], [12, 13, 14],
  [16, 17, 18], [17, 18, 19], [0, 4, 12], [1, 3, 6], [2, 5, 9],
  [6, 11, 16], [7, 12, 17], [8, 13, 18], [9, 14, 18],
  [3, 7, 12], [5, 8, 12]
];

export class PuliMekaEngine {
  state: GameState;

  constructor() {
    this.state = this.getInitialState();
  }

  getInitialState(): GameState {
    const board: BoardPosition[] = Array(23).fill(null);
    board[0] = 'T';
    board[1] = 'T';
    board[2] = 'T';

    return {
      board,
      goatsToPlace: 15,
      goatsCaptured: 0,
      turn: 'G',
      gameOver: false,
      winner: null
    };
  }

  placeGoat(pos: number): { success: boolean; capture?: number } {
    if (this.state.gameOver || this.state.turn !== 'G' || this.state.goatsToPlace <= 0) return { success: false };
    if (pos < 0 || pos > 22 || this.state.board[pos] !== null) return { success: false };

    this.state.board[pos] = 'G';
    this.state.goatsToPlace--;
    this.state.turn = 'T';
    this.checkWinCondition();
    return { success: true };
  }

  movePiece(player: Player, start: number, end: number): { success: boolean; capture?: number } {
    if (this.state.gameOver || this.state.turn !== player) return { success: false };
    if (start < 0 || start > 22 || end < 0 || end > 22) return { success: false };
    if (this.state.board[start] !== player || this.state.board[end] !== null) return { success: false };

    // 1. Normal Move
    if (ADJACENCY[start]?.includes(end)) {
      this.state.board[start] = null;
      this.state.board[end] = player;
      this.state.turn = player === 'G' ? 'T' : 'G';
      this.checkWinCondition();
      return { success: true };
    }

    // 2. Jump Move (Tiger Only)
    if (player === 'T') {
      for (const [s, m, e] of LINEAR_JUMPS) {
        if ((start === s && end === e) || (start === e && end === s)) {
          const mid = m;
          if (this.state.board[mid] === 'G') {
            this.state.board[start] = null;
            this.state.board[mid] = null;
            this.state.board[end] = 'T';
            this.state.goatsCaptured++;
            this.state.turn = 'G';
            this.checkWinCondition();
            return { success: true, capture: mid };
          }
        }
      }
    }

    return { success: false };
  }

  private checkWinCondition() {
    // Tiger Win
    if (this.state.goatsCaptured >= 5) {
      this.state.gameOver = true;
      this.state.winner = 'Tigers';
      return;
    }

    // Goat Win: Check if any Tiger has a move
    if (this.state.turn === 'T') {
      let anyTigerCanMove = false;
      for (let i = 0; i < 23; i++) {
        if (this.state.board[i] === 'T') {
          if (this.hasMovesAtPos('T', i)) {
            anyTigerCanMove = true;
            break;
          }
        }
      }
      if (!anyTigerCanMove) {
        this.state.gameOver = true;
        this.state.winner = 'Goats';
      }
    }
  }

  private hasMovesAtPos(player: Player, pos: number): boolean {
    // Check adjacent
    const neighbors = ADJACENCY[pos] || [];
    for (const n of neighbors) {
      if (this.state.board[n] === null) return true;
    }

    // Check jumps
    if (player === 'T') {
      for (const [s, m, e] of LINEAR_JUMPS) {
        if (pos === s && this.state.board[m] === 'G' && this.state.board[e] === null) return true;
        if (pos === e && this.state.board[m] === 'G' && this.state.board[s] === null) return true;
      }
    }
    return false;
  }
}
