import React from 'react';
import PropTypes from 'prop-types';

// Recompose
import { compose } from 'recompose';

// Router
import {
  Switch,
  Route,
  Redirect,
} from 'react-router-dom';

// Material-UI
import { withStyles } from 'material-ui/styles';

// Lodash
// import has from 'lodash/has';

// Project
import withRoot from '../withRoot';
// import withProps from '../withProps';
import AppFrame from '../modules/components/AppFrame';

// Project Views
import NotFound from './NotFound/NotFound';
import ScheduleEdit from './Schedule/ScheduleEdit';
import ScheduleList from './Schedule/ScheduleList';
import ScheduleCreate from './Schedule/ScheduleCreate';


const styles = theme => ({
  '@global': {
    'html, body, #root': {
      height: '100%',
    }
  },
  root: {
    // height: '100%',
  },
});

class Index extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {

    }
  }


  componentDidMount() {
  }

  render() {
    const { classes } = this.props;

    return (
      <AppFrame className={classes.root}>
        <Switch>
          <Route exact path="/" render={() => <Redirect to="/schedules/browser" />} />
          {/* <Route exact path="/login" component={withProps(Login, { user })} /> */}
          <Route exact path="/schedules/create" component={ScheduleCreate} />
          <Route exact path="/schedules/browser" component={ScheduleList} />
          <Route exact path="/schedules/browser/:schedule" component={ScheduleEdit} />

          <Route component={NotFound} />
        </Switch>
      </AppFrame>
    );
  }
}

Index.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default compose(
  withRoot,
  withStyles(styles),
)(Index);