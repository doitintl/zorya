import React from 'react';

// Material UI
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';

const styles = theme => ({
  root: {
    padding: theme.spacing.unit,
  },
});

class NotFound extends React.Component {
  render() {
    const { classes, location } = this.props;

    return (
      <div className={classes.root}>
        <Typography variant="subheading" color="error">
          Not Found: <code>{location.pathname}</code>
        </Typography>
      </div>
    );
  }
}

export default withStyles(styles)(NotFound);
