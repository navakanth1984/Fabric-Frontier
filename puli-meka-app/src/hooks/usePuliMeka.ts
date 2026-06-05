import { useState, useCallback, useRef } from 'react';
import { PuliMekaEngine, GameState, Player } from '../logic/engine';

export const usePuliMeka = () => {
  const engineRef = useRef(new PuliMekaEngine());
  const [gameState, setGameState] = useState<GameState>(engineRef.current.state);

  const placeGoat = useCallback((pos: number) => {
    const result = engineRef.current.placeGoat(pos);
    if (result.success) {
      setGameState({ ...engineRef.current.state });
    }
    return result;
  }, []);

  const movePiece = useCallback((player: Player, start: number, end: number) => {
    const result = engineRef.current.movePiece(player, start, end);
    if (result.success) {
      setGameState({ ...engineRef.current.state });
    }
    return result;
  }, []);

  const resetGame = useCallback(() => {
    engineRef.current = new PuliMekaEngine();
    setGameState(engineRef.current.state);
  }, []);

  return {
    gameState,
    placeGoat,
    movePiece,
    resetGame,
  };
};
