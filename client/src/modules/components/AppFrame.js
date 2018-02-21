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
import IconButton from 'material-ui/IconButton';
import Hidden from 'material-ui/Hidden';
import MenuIcon from 'material-ui-icons/Menu';

// Lodash
import map from 'lodash/map';
import find from 'lodash/find';
import startsWith from 'lodash/startsWith';

// Project
import logo from '../../assets/zorya.png';

const drawerWidth = 200;

const links = [
  {
    primary: "Schedules",
    path: "/schedules/browser",
    icon: <ScheduleIcon />
  },
  {
    primary: "Policies",
    path: "/policies/browser",
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
    marginLeft: drawerWidth,
    [theme.breakpoints.up('md')]: {
      width: `calc(100% - ${drawerWidth}px)`,
    },
  },
  navIconHide: {
    [theme.breakpoints.up('md')]: {
      display: 'none',
    },
  },
  drawerHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: 112,
    [theme.breakpoints.up('sm')]: {
      height: 128,
    },
  },
  drawerPaper: {
    width: drawerWidth,
    [theme.breakpoints.up('md')]: {
      position: 'relative',
      height: '100%',
    },
  },
  drawerDocked: {
    height: '100%',
  },
  content: {
    backgroundColor: theme.palette.background.default,
    width: '100%',
    // padding: theme.spacing.unit,
    // overflow: 'hidden',
    height: 'calc(100% - 56px)',
    marginTop: 56,
    [theme.breakpoints.up('sm')]: {
      height: 'calc(100% - 64px)',
      marginTop: 64,
    },
  },
});

class AppFrame extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      title: "",
      mobileOpen: false
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

  handleDrawerToggle = () => {
    this.setState((prevState, props) => ({ mobileOpen: !prevState.mobileOpen }));
  };

  render() {
    const { classes, history, children } = this.props;
    const { title, mobileOpen } = this.state;

    const drawer = (
      <div>
        <div className={classes.drawerHeader}>
          <img src={logo} alt="Zorya" />
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
      </div>
    );

    return (
      <div className={classes.root}>
        <AppBar position="absolute" color="primary" className={classes.appBar} elevation={0} square>
          <Toolbar>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              onClick={this.handleDrawerToggle}
              className={classes.navIconHide}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="title" color="inherit" noWrap>
              {title}
            </Typography>
          </Toolbar>
        </AppBar>

        <Hidden mdUp>
          <Drawer
            variant="temporary"
            anchor="left"
            open={mobileOpen}
            classes={{
              paper: classes.drawerPaper,

            }}
            onClose={this.handleDrawerToggle}
            ModalProps={{
              keepMounted: true, // Better open performance on mobile.
            }}
          >
            {drawer}
          </Drawer>
        </Hidden>

        <Hidden smDown implementation="css">
          <Drawer
            variant="permanent"
            anchor="left"
            open
            classes={{
              paper: classes.drawerPaper,
              docked: classes.drawerDocked
            }}
          >
            {drawer}
          </Drawer>
        </Hidden>

        <main className={classes.content}>
          {children}
        </main>

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