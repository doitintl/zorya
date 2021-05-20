import React from 'react';
import PropTypes from 'prop-types';

// Material UI
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';

const styles = (theme) => ({
  root: {
    height: '100%',
  },
  button: {
    marginRight: theme.spacing(2),
  },
});

class ErrorAlert extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.onClose = props.onClose;
  }

  render() {
    const { classes, showError, errorTitle, errorMessage } = this.props;

    return (
      <div className={classes.root}>
        <Dialog
          open={showError}
          onClose={this.onClose}
          aria-labelledby="alert-dialog-title"
          aria-describedby="alert-dialog-description"
        >
          <DialogTitle id="alert-dialog-title">{errorTitle}</DialogTitle>
          <DialogContent>
            <DialogContentText id="alert-dialog-description">
              {errorMessage}
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={this.onClose} color="primary" autoFocus>
              OK
            </Button>
          </DialogActions>
        </Dialog>
      </div>
    );
  }
}
ErrorAlert.propTypes = {
  showError: PropTypes.bool.isRequired,
  errorTitle: PropTypes.string,
  errorMessage: PropTypes.string,
  onClose: PropTypes.func.isRequired,
};

export default withStyles(styles)(ErrorAlert);
