import React from 'react';

// Router
import { BrowserRouter } from 'react-router-dom';

// Material-UI
import { MuiThemeProvider, createMuiTheme } from 'material-ui/styles';
import lightGreen from 'material-ui/colors/lightGreen';
import pink from 'material-ui/colors/pink';
import Reboot from 'material-ui/Reboot';

// Material-UI Theme
const theme = createMuiTheme({
  palette: {
    primary: {
      light: lightGreen[300],
      main: lightGreen[500],
      dark: lightGreen[700],
    },
    secondary: {
      light: pink[300],
      main: pink[500],
      dark: pink[700],
    },
    type: 'dark'
  }
});

// Expose the theme as a global variable.
if (process.browser) {
  console.log(theme);
  window.theme = theme;
}

const withRoot = Component => props =>
  (<MuiThemeProvider theme={theme}>
    <Reboot />
    <BrowserRouter>
      <Component {...props} />
    </BrowserRouter>
  </MuiThemeProvider>);


export default withRoot;