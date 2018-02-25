import React from 'react';

// Material UI
import { withStyles } from 'material-ui/styles';
// import Typography from 'material-ui/Typography';

const styles = theme => ({
  root: {
    overflow: 'auto',
    padding: theme.spacing.unit * 2,
    height: 'calc(100% - 56px)',
    [theme.breakpoints.up('sm')]: {
      height: 'calc(100% - 64px)',
    },
  },
});

class AppPageContent extends React.Component {
  render() {
    const { classes, children } = this.props;

    return (
      <div className={classes.root}>
        {children}
      </div>
    )
  }
}

export default withStyles(styles)(AppPageContent);
