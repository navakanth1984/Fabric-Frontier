import React from 'react';
import { View, StyleSheet } from 'react-native';
import { GameBoard } from '../../src/components/GameBoard';

export default function GameScreen() {
  return (
    <View style={styles.container}>
      <GameBoard />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
});
