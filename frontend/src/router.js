import React from 'react';
import { Router, Route, Switch } from 'dva/router';
import TtsPage from "./pages/TtsPage";

function RouterConfig({ history }) {
  return (
    <Router history={history}>
      <Switch>
        <Route path="*" component={TtsPage} />
      </Switch>
    </Router>
  );
}

export default RouterConfig;
