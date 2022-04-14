import React, { PureComponent } from 'react';
import {Stack} from "office-ui-fabric-react";
import {initializeIcons} from '@uifabric/icons';
import TtsGenerator from "../components/TtsGenerator";
initializeIcons("./icons/fonts/");

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
