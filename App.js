import React from 'react';

import {
  NavigationContainer,
} from '@react-navigation/native';

import Routes from './src/routes/app.routes';

export default function App() {
  return (
    <NavigationContainer>
      <Routes />
    </NavigationContainer>
  );
}