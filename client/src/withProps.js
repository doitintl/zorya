import React from 'react';

const withProps = (Component, componentProps) => {
  return class Route extends React.Component {
    render() {
      let props = Object.assign({}, this.props, componentProps);
      return <Component {...props} />;
    }
  };
};

export default withProps;
