import React from 'react';

// Material UI
import { withStyles } from '@material-ui/core/styles';
import Divider from '@material-ui/core/Divider';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';

const styles = (theme) => ({
  appBar: {
    backgroundColor: theme.palette.background.default,
  },
});

class AppPageActions extends React.Component {
  render() {
    const { classes, children } = this.props;

    return (
      <div>
        <AppBar
          position="static"
          color="inherit"
          className={classes.appBar}
          elevation={0}
          square
        >
          <Toolbar>{children}</Toolbar>
        </AppBar>
        <Divider />
      </div>
    );
  }
}

export default withStyles(styles)(AppPageActions);
