import React from 'react';

// Router
import { BrowserRouter } from 'react-router-dom';

// Material-UI
import { MuiThemeProvider, createMuiTheme } from 'material-ui/styles';
import blue from 'material-ui/colors/blue';
// import pink from 'material-ui/colors/pink';
import Reboot from 'material-ui/Reboot';

// Material-UI Theme
const theme = createMuiTheme({
  palette: {
    primary: {
      light: blue[500],
      main: blue[700],
      dark: blue[900],
    },
    secondary: {
      light: blue[500],
      main: blue[700],
      dark: blue[900],
    },
    type: 'light'
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