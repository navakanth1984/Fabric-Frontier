import { Redirect } from 'expo-router';

export default function Index() {
  // Check if user is logged in (placeholder)
  // For now, redirect to game (tabs)
  return <Redirect href="/(tabs)" />;
}
