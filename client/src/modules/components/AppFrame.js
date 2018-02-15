import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

// Recompose
import { compose } from 'recompose';

// Router
import {
  withRouter,
} from 'react-router-dom';

import { withStyles } from 'material-ui/styles';
import Drawer from 'material-ui/Drawer';
import AppBar from 'material-ui/AppBar';
import Toolbar from 'material-ui/Toolbar';
import List from 'material-ui/List';
import Typography from 'material-ui/Typography';
import Divider from 'material-ui/Divider';
import { ListItem, ListItemIcon, ListItemText } from 'material-ui/List';
import ScheduleIcon from 'material-ui-icons/Schedule';
import PolicyIcon from 'material-ui-icons/LibraryBooks';

// Lodash
import map from 'lodash/map';
import find from 'lodash/find';
import startsWith from 'lodash/startsWith';

const drawerWidth = 200;

const links = [
  {
    primary: "Schedules",
    path: "/schedules",
    icon: <ScheduleIcon />
  },
  {
    primary: "Policies",
    path: "/policies",
    icon: <PolicyIcon />
  },
]

const styles = theme => ({
  root: {
    width: '100%',
    height: '100%',
    zIndex: 1,
    overflow: 'hidden',
    display: 'flex',
  },
  appBar: {
    // position: 'absolute',
    width: `calc(100% - ${drawerWidth}px)`,
    marginLeft: drawerWidth,
  },
  drawerPaper: {
    position: 'relative',
    height: '100%',
    width: drawerWidth,
  },
  drawerHeader: {
    ...theme.mixins.toolbar,
    display: 'flex',
    alignItems: 'center',
    padding: `0 ${theme.spacing.unit * 3}px`
  },
  content: {
    overflow: 'auto',
    backgroundColor: theme.palette.background.default,
    width: '100%',
    padding: theme.spacing.unit,
    height: 'calc(100% - 56px)',
    marginTop: 56,
    [theme.breakpoints.up('sm')]: {
      height: 'calc(100% - 64px)',
      marginTop: 64,
    },
  },
  highlight: {
    backgroundColor: theme.palette.action.selected,
  }
});

class AppFrame extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      title: ""
    }
  }

  componentDidMount() {
    const { history } = this.props;
    const currentLink = find(links, link => startsWith(history.location.pathname, link.path));
    if (currentLink) {
      this.setState({
        title: currentLink.primary
      })
    }
    
  }

  handleClickLink = link => event => {
    const { history } = this.props;
    history.push(link.path);
    this.setState({
      title: `${link.primary}`
    })
  }

  render() {
    const { classes, history, children } = this.props;
    const { title } = this.state;

    const drawer = (
      <Drawer
        variant="permanent"
        classes={{
          paper: classes.drawerPaper,
        }}
        anchor="left"
      >
        <div className={classes.drawerHeader}>
          <Typography variant="headline" color="secondary">
            Zorya logo
          </Typography>
        </div>

        <Divider />
        <List dense disablePadding>
          {
            map(links, (link, index) =>
              <ListItem key={index} className={classNames({ [classes.highlight]: startsWith(history.location.pathname, link.path) })} button onClick={this.handleClickLink(link)}>
                <ListItemIcon>
                  {link.icon}
                </ListItemIcon>
                <ListItemText primary={link.primary} />
              </ListItem>
            )
          }
        </List>
      </Drawer>
    );

    return (
      <div className={classes.root}>

        <AppBar position="absolute" className={classes.appBar}>
          <Toolbar>
            <Typography variant="title" color="inherit" noWrap>
              {title}
            </Typography>
          </Toolbar>
        </AppBar>

        {drawer}

        <div className={classes.content}>
          {children}
        </div>

      </div>
    );
  }
}

AppFrame.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default compose(
  withRouter,
  withStyles(styles),
)(AppFrame);