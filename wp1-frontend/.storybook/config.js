import { configure } from '@storybook/vue';

// Bootstrap is used for all component styles.
import 'bootstrap/dist/css/bootstrap.css';

// automatically import all files ending in *.stories.js
configure(require.context('../stories', true, /\.stories\.js$/), module);
