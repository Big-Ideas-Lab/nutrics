const functions = require('firebase-functions');
const admin = require('firebase-admin');
const fetch = require('node-fetch');

admin.initializeApp();

async function getData(change,context) {
    const data = change.after.data();
    const previousData = change.before.data();

    // We'll only update if the LOCATION has changed.
    // This is crucial to prevent infinite loops.
    // if (data.location[0] === previousData.location[0]) return null;

    //Get lat and lon from the change. Get 4 recs for now. 
    const lat = data.location[0];
    const lon = data.location[1];
    const likes = data.liked;
    const distance = 100;

    json_file = {"latitude": lat, "longitude": lon, "distance": distance, "user_hx": likes}

    fetch('https://nutrics.appspot.com/get_rec', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(json_file),
      }).then((response) => response.json()).then((data) => {
        console.log('Success:', data);
        const json = data;
        return change.after.ref.set({
              recs: json,
          }, {merge: true});
      })
      .catch((error) => {
        console.error('Error:', error);
      });
    
  }


exports.getRecs = functions.firestore
    .document('users/{userId}')
    .onUpdate(getData);
