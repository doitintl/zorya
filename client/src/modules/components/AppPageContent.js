import React from 'react';
import PropTypes from 'prop-types';

// Material UI
import { withStyles } from '@material-ui/core/styles';
import CircularProgress from '@material-ui/core/CircularProgress';

// Project
import ErrorAlert from './ErrorAlert';

const styles = (theme) => ({
  root: {
    overflow: 'auto',
    padding: theme.spacing(2),
    height: 'calc(100% - 56px)',
    [theme.breakpoints.up('sm')]: {
      height: 'calc(100% - 64px)',
    },
  },
  centered: {
    position: 'absolute',
    left: '50%',
    top: '50%',
  },
});

class AppPageContent extends React.Component {
  render() {
    const { classes, children } = this.props;

    const {
      showBackendError,
      showLoadingSpinner,
      backendErrorTitle = 'An Error Occurred:',
      backendErrorMessage = 'Unspecified error, check logs.',
      onBackendErrorClose,
    } = this.props;

    return (
      <div className={classes.root}>
        {showLoadingSpinner ? (
          <CircularProgress classes={{ root: classes.centered }} />
        ) : (
          children
        )}
        <ErrorAlert
          showError={showBackendError}
          errorTitle={backendErrorTitle}
          errorMessage={backendErrorMessage}
          onClose={onBackendErrorClose}
        />
      </div>
    );
  }
}

AppPageContent.propTypes = {
  showBackendError: PropTypes.bool.isRequired,
  showLoadingSpinner: PropTypes.bool,
  backendErrorTitle: PropTypes.string,
  backendErrorMessage: PropTypes.string,
  onBackendErrorClose: PropTypes.func.isRequired,
};

export default withStyles(styles)(AppPageContent);
