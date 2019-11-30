import { storiesOf } from '@storybook/vue';
import fetchMock from 'fetch-mock';

import Autocomplete from '../src/components/Autocomplete';

const payload = [
  {
    name: 'Airplanes',
    last_updated: '20190101000000',
  },
  {
    name: 'Airplane crashes',
    last_updated: '20190101000000',
  },
  {
    name: 'Alphabet',
    last_updated: '20190101000000',
  },
  {
    name: 'Alpine Skiing',
    last_updated: '20190101000000',
  },
  {
    name: 'Austria',
    last_updated: '20190101000000',
  },
  {
    name: 'Australia',
    last_updated: '20190101000000',
  },
  {
    name: 'Australian Sports',
    last_updated: '20190101000000',
  },
]

storiesOf('Autocomplete', module)
  .add('default', () => {
    fetchMock
      .restore()
      .getOnce(
        'http://localhost:5000/v1/projects/',
        payload,
      );

    return {
      components: {Autocomplete},
      template: '<div style="width: 500px"><Autocomplete/></div>',
      data: () => {return {};},
    }
  });
