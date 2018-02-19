import React from 'react';

// Material UI
import { withStyles } from 'material-ui/styles';
// import Typography from 'material-ui/Typography';
import Divider from 'material-ui/Divider';
import AppBar from 'material-ui/AppBar';
import Toolbar from 'material-ui/Toolbar';

const styles = theme => ({
  appBar: {
    backgroundColor: theme.palette.background.default
  },
});

class AppPageActions extends React.Component {
  render() {
    const { classes, children } = this.props;

    return (
      <div>
        <AppBar position="static" color="inherit" className={classes.appBar} elevation={0} square>
          <Toolbar>
            {children}

          </Toolbar>
        </AppBar>
        <Divider />
      </div>
    )
  }
}

export default withStyles(styles)(AppPageActions);
