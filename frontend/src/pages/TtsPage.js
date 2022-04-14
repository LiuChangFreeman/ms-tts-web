import React, { PureComponent } from 'react';
import {Stack} from "office-ui-fabric-react";
import TtsGenerator from "../components/TtsGenerator";

class TtsPage extends PureComponent {

  render() {
    return (
      <Stack
        horizontal
        horizontalAlign="center"
        verticalAlign="start"
      >
        <TtsGenerator/>
      </Stack>
    );
  }
}

export default TtsPage;
