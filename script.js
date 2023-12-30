function mainPage() {
    let loginContainer = document.getElementById("login-container");
    let tweetContainer = document.getElementById("tweet-container");
    let tweetList = document.getElementById("tweet-list");

    // check if cookie exists
    if (document.cookie.indexOf("username=") !== -1) {
      // The cookie exists
      loginContainer.innerHTML = "";

      tweetContainer.innerHTML = `<form id="new-tweet"> <label for="new-tweet">Add a new Tweet!</label><br> <input type="text" id="new-twt" value=" " name="new-twt"><input type="submit" id="add-tweet" value="Send it!" onClick="addTwt()"></form><input type="submit" value="Log out" onClick="logout()"><H2>Tweets</H2>
      <form id="imageForm" enctype="multipart/form-data">
      <input type="file" id="imageInput" accept="image/*" required>
      <button type="button" onclick="uploadImage()">Upload Image</button>
      </form>`;

      getTweets();
    } else {
      loginContainer.innerHTML = `<form id="login-form">
        <label for="use-name">Username</label><br>
        <input type="text" id="username" name="username" value=""><br>
        <label for="password">Password</label><br>
        <input type="text" id="password" name="password" value=""><br><br>
        <input type="button" id="login-btn" value="Log in" onClick="login(this.form)">
        </form>`;

      tweetContainer.innerHTML = "";
      tweetList.innerHTML = "";
    }
  }

  function login(form) {
    var loginReq = new XMLHttpRequest();
    //var loginForm = document.getElementById("login-form");
    loginReq.onreadystatechange = function () {
      if (this.readyState == 4 && this.status == 200) {
        // parse the response text as JSON
        var data = loginReq.responseText;
        console.log(data);
        // The cookie exists
        mainPage();
      }
    };

    loginReq.open("POST", "/api/login");
    loginReq.setRequestHeader("Content-type", "application/json");
    loginReq.send(
      JSON.stringify({
        user: form.username.value,
        pass: form.password.value,
      })
    );
  }

  function getTweets() {
    var getTweetReq = new XMLHttpRequest();

    let tweetList = document.getElementById("tweet-list");
    getTweetReq.onreadystatechange = function () {
      if (this.readyState == 4 && this.status == 200) {
        var data = JSON.parse(getTweetReq.responseText);

        if (data !== undefined) {
          var tweet_str = '<ul>';
          for (var i = 0; i < data.length; i++) {
            var tweet = data[i];
            //console.log(getSessionId())
            if (tweet.username === getSessionId()) {
              tweet_str += buildTweetDel(
                tweet.tweet_str,
                tweet.username,
                tweet.tweet_id
              );
            } else {
              tweet_str += buildTweet(tweet.tweet_str, tweet.username);
            }
          }

          tweet_str += "</ul>";
          tweetList.innerHTML = tweet_str;
        }
      }
    };
    getTweetReq.open("GET", "/api/tweet");

    getTweetReq.send();
  }

  function addTwt() {
    event.preventDefault();

    // Get the tweet text from the input field
    let tweetText = document.getElementById("new-twt");
    // Get the username from the session cookie
    var username = getSessionId();
    var twt = tweetText.value;

    if (twt === undefined) {
      return;
    }

    // Generate a new tweet object with a unique ID
    var newTweet = {
      tweet_id: -1, // arbitrary, will fix in server
      tweet_str: twt,
      username: username,
    };

    var addTweetReq = new XMLHttpRequest();
    addTweetReq.onreadystatechange = function () {
      if (this.readyState == 4 && this.status == 200) {
        // reload the page, but not really
        mainPage();
      }
    };

    addTweetReq.open("POST", "/api/tweet");
    addTweetReq.setRequestHeader("Content-type", "application/json");
    console.log(JSON.stringify(newTweet));
    addTweetReq.send(JSON.stringify(newTweet));
  }

  function deleteTweet(index) {
    var deleteTwt = new XMLHttpRequest();

    deleteTwt.onreadystatechange = function () {
      if (this.readyState == 4 && this.status == 200) {
        // reload the page, but not really
        mainPage();
      }
    };

    deleteTwt.open("DELETE", `/api/tweet/${index}`);
    deleteTwt.setRequestHeader("Content-type", "text/html");
    deleteTwt.send(index);
  }

  function logout() {
    event.preventDefault();

    logoutReq = new XMLHttpRequest();

    //document.cookie = `username=-1; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/`;
    logoutReq.onreadystatechange = function () {
      if (this.readyState == 4 && this.status == 200) {
        mainPage();
      }
    };

    logoutReq.open("DELETE", "/api/login");
    logoutReq.setRequestHeader("Content-type", "text/html");
    logoutReq.send();
  }

  mainPage();
  // Helper Functions

  function buildTweet(tweet, user) {
    return (
      "<li class=\"tweet-post\"" +
      '<span style="margin-right: 20px;">' +
      tweet +
      "</span>" +
      '<span style="margin-right: 20px;">' +
      user +
      "</span></li>"
    );
  }

  function buildTweetDel(tweet, user, id) {
    return (
      "<li class=\"tweet-post\">" +
      '<span style="margin-right: 20px;">' +
      tweet +
      "</span>" +
      '<span style="margin-right: 20px;">' +
      user +
      "</span>" +
      '<input class="delete-button" type="button" id="deleteButton-' +
      id +
      '" value="DELETE" onClick="deleteTweet(' +
      id +
      ')">' +
      "</li>"
    );
  }

  function getSessionId() {
    var name = "username=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var cookieArray = decodedCookie.split(";");

    for (var i = 0; i < cookieArray.length; i++) {
      var cookie = cookieArray[i];
      while (cookie.charAt(0) == " ") {
        cookie = cookie.substring(1);
      }
      if (cookie.indexOf(name) == 0) {
        return cookie.substring(name.length, cookie.length);
      }
    }

    return "";
  }

  function uploadImage() {
    var fileInput = document.getElementById('imageInput');
    var file = fileInput.files[0];

    if (file) {
        var formData = new FormData();
        formData.append('image', file);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/images');

        xhr.onreadystatechange = function () {
          if (this.readyState == 4 && this.status == 200) {
            // reload the page, but not really
            mainPage();
          }
        };

        xhr.send(formData);
    }

  }