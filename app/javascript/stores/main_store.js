import axios from 'axios';
import { defineStore } from 'pinia'

// TODO: use the last location that the user was in, as the default
// the first argument is a unique id of the store across your application
export const useMainStore = defineStore('main', {
  state: () => ({
    center: {lat: 51.093048, lng: 6.842120},
    zoom: 7,
    focusTab: 'events',
    signedIn: false
  }),
  actions: {
    async isSignedIn() {
      let token = document.getElementsByName('csrf-token')[0].getAttribute('content')
      axios.defaults.headers.common['X-CSRF-Token'] = token
      axios.defaults.headers.common['Accept'] = 'application/json'

      await axios.get(
        `/registrations/is_signed_in.json`
      ).then((response) => {
        signedIn = response.data.isSignedIn

      }).
        catch((blah) => {
         console.log('Fail', blah);
          // TODO: display error
        });

      console.log(signedIn)
    },
    setGMapsPlace(center) {
      this.center = center
      this.zoom = 15;
    },
    setFocusTab(tabToFocus) {
      this.focusTab = 'event'
    }
  }
});
