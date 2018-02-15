import React from 'react';
import classNames from 'classnames';

// Material UI
import { withStyles } from 'material-ui/styles';
import Typography from 'material-ui/Typography';
// import Divider from 'material-ui/Divider';
import Grid from 'material-ui/Grid';
import Paper from 'material-ui/Paper';

// Lodash
import map from 'lodash/map';

// Project
import ScheduleService from '../../modules/api/schedule';

const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

const styles = theme => ({
  root: {
    padding: theme.spacing.unit,
  },
  boxSize: {
    height: '36px',
    width: '36px',
  },
  longBoxSize: {
    height: '36px',
    width: '100px',
  },
  boxContent: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  on: {
    backgroundColor: theme.palette.primary.main,
  },
  off: {
    backgroundColor: theme.palette.secondary.light,
  }
});

class Schedule extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      schedule: null,
      matrix: null,
    }

    this.scheduleService = new ScheduleService();
  }

  async componentDidMount() {
    const { match } = this.props;
    const schedule = await this.scheduleService.get(match.params.schedule);
    console.log(schedule.__ndarray__);
    this.setState({
      schedule,
      matrix: schedule.__ndarray__
    });
  }

  getDayGrid = (dayIndex, dayValues) => {
    const { classes } = this.props;

    const hourBlocks = map(dayValues, (value, index) => (
      <Grid key={`day-${dayIndex}-hour-${index}`} item>
        {
          value ?
            (
              <Paper className={classNames(classes.boxSize, classes.on)} elevation={2} />
            ) : (
              <Paper className={classNames(classes.boxSize)} elevation={2} />
            )
        }
      </Grid>
    ))

    return [
      <Grid key={`day-${dayIndex}`} item>
        <div className={classNames(classes.longBoxSize, classes.boxContent)}>
          <Typography variant="caption" color="textSecondary">
            {days[dayIndex]}
          </Typography>
        </div>
      </Grid>,
      ...hourBlocks
    ]
  }

  render() {
    const { classes } = this.props;
    const { schedule } = this.state;

    const hours = [...Array(25).keys()];

    return (

      schedule &&
      <div className={classes.root}>
        {/* <Typography variant="subheading" color="textSecondary" gutterBottom>
          {match.params.schedule}
          <Divider />
        </Typography> */}

        <Typography variant="body2" color="textSecondary">
          Name: {schedule.name}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Timezone: {schedule.timezone}
        </Typography>


        <Grid container justify="center" spacing={8}>

          <Grid container item wrap="nowrap">
            {
              map(hours, hour =>
                <Grid key={`hour-${hour}`} item>
                  {hour > 0 ?
                    (
                      <div className={classNames(classes.boxSize, classes.boxContent)}>
                        <Typography variant="caption" color="textSecondary">
                          {
                            hour <= 10 ? `0${hour - 1}` : hour - 1
                          }
                        </Typography>
                      </div>
                    ) : (
                      <div className={classNames(classes.longBoxSize, classes.boxContent)}>
                        <Typography variant="caption" color="textSecondary">
                          Hours =>
                        </Typography>
                      </div>
                    )
                  }
                </Grid>)
            }
          </Grid>


          {
            map(schedule.__ndarray__, (dayValues, dayIndex) =>
              <Grid key={`${dayIndex}`} container item>
                {this.getDayGrid(dayIndex, dayValues)}
              </Grid>)
          }
        </Grid>


      </div>

    )
  }
}

export default withStyles(styles)(Schedule);

