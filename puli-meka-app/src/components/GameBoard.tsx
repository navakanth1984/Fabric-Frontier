import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Dimensions } from 'react-native';
import Svg, { Line, Circle } from 'react-native-svg';
import { usePuliMeka } from '../hooks/usePuliMeka';
import { ADJACENCY } from '../logic/engine';

const { width } = Dimensions.get('window');
const BOARD_SIZE = Math.min(width - 40, 500);
const PADDING = 40;

// Coordinate mapping for 23 positions (approximate triangular grid)
const POSITIONS: Record<number, { x: number; y: number }> = {
  0: { x: 0.5, y: 0.05 },
  1: { x: 0.4, y: 0.2 }, 2: { x: 0.6, y: 0.2 },
  3: { x: 0.3, y: 0.35 }, 4: { x: 0.5, y: 0.35 }, 5: { x: 0.7, y: 0.35 },
  6: { x: 0.2, y: 0.5 }, 7: { x: 0.4, y: 0.5 }, 8: { x: 0.6, y: 0.5 }, 9: { x: 0.8, y: 0.5 },
  10: { x: 0.9, y: 0.5 },
  11: { x: 0.1, y: 0.65 }, 12: { x: 0.3, y: 0.65 }, 13: { x: 0.5, y: 0.65 }, 14: { x: 0.7, y: 0.65 }, 15: { x: 0.9, y: 0.65 },
  16: { x: 0.05, y: 0.85 }, 17: { x: 0.25, y: 0.85 }, 18: { x: 0.45, y: 0.85 }, 19: { x: 0.65, y: 0.85 }, 20: { x: 0.85, y: 0.85 },
  21: { x: 0.5, y: 0.95 }, 22: { x: 0.7, y: 0.95 }
};

export const GameBoard = () => {
  const { gameState, placeGoat, movePiece } = usePuliMeka();
  const [selectedPos, setSelectedPos] = useState<number | null>(null);

  const handlePress = (pos: number) => {
    if (gameState.gameOver) return;

    if (gameState.turn === 'G' && gameState.goatsToPlace > 0) {
      placeGoat(pos);
    } else {
      if (selectedPos === null) {
        if (gameState.board[pos] === gameState.turn) {
          setSelectedPos(pos);
        }
      } else {
        if (pos === selectedPos) {
          setSelectedPos(null);
        } else {
          const result = movePiece(gameState.turn, selectedPos, pos);
          if (result.success) {
            setSelectedPos(null);
          } else if (gameState.board[pos] === gameState.turn) {
            setSelectedPos(pos);
          }
        }
      }
    }
  };

  const renderLines = () => {
    const lines: JSX.Element[] = [];
    Object.entries(ADJACENCY).forEach(([startStr, neighbors]) => {
      const start = parseInt(startStr);
      neighbors.forEach((end) => {
        if (start < end) {
          lines.push(
            <Line
              key={`${start}-${end}`}
              x1={POSITIONS[start].x * BOARD_SIZE}
              y1={POSITIONS[start].y * BOARD_SIZE}
              x2={POSITIONS[end].x * BOARD_SIZE}
              y2={POSITIONS[end].y * BOARD_SIZE}
              stroke="#555"
              strokeWidth="2"
            />
          );
        }
      });
    });
    return lines;
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Puli Meka</Text>
        <Text style={styles.status}>
          {gameState.gameOver 
            ? `Winner: ${gameState.winner}` 
            : `${gameState.turn === 'G' ? 'Goat' : 'Tiger'}'s Turn`}
        </Text>
        <Text style={styles.stats}>
          Goats: {15 - gameState.goatsToPlace}/15 | Captured: {gameState.goatsCaptured}
        </Text>
      </View>

      <View style={{ width: BOARD_SIZE, height: BOARD_SIZE, alignSelf: 'center' }}>
        <Svg width={BOARD_SIZE} height={BOARD_SIZE}>
          {renderLines()}
          {Object.entries(POSITIONS).map(([posStr, coord]) => {
            const pos = parseInt(posStr);
            const piece = gameState.board[pos];
            const isSelected = selectedPos === pos;

            return (
              <Circle
                key={pos}
                cx={coord.x * BOARD_SIZE}
                cy={coord.y * BOARD_SIZE}
                r="15"
                fill={piece === 'T' ? '#e74c3c' : piece === 'G' ? '#f1c40f' : '#ddd'}
                stroke={isSelected ? '#2ecc71' : 'none'}
                strokeWidth="4"
                onPress={() => handlePress(pos)}
              />
            );
          })}
        </Svg>
      </View>

      <View style={styles.instructions}>
        <Text style={styles.instructionText}>
          {gameState.turn === 'G' && gameState.goatsToPlace > 0 
            ? "Click an empty circle to place a Goat."
            : "Click a piece to select, then an empty circle to move."}
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: '#fff',
    flex: 1,
  },
  header: {
    alignItems: 'center',
    marginBottom: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  status: {
    fontSize: 18,
    color: '#333',
    marginVertical: 5,
  },
  stats: {
    fontSize: 14,
    color: '#666',
  },
  instructions: {
    marginTop: 20,
    padding: 15,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
  },
  instructionText: {
    textAlign: 'center',
    color: '#444',
  },
});
