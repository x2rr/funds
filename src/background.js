import axios from "axios";

var Interval;
var holiday;
var getHoliday = () => {
  let url = "https://x2rr.github.io/funds/holiday.json";
  return axios.get(url);
};
var checkHoliday = date => {
  var nowMonth = date.getMonth() + 1;
  var nowYear = date.getFullYear();
  var strDate = date.getDate();
  if (nowMonth >= 1 && nowMonth <= 9) {
    nowMonth = "0" + nowMonth;
  }
  if (strDate >= 0 && strDate <= 9) {
    strDate = "0" + strDate;
  }

  let check = false;
  var nowDate = nowMonth + "-" + strDate;
  let holidayList = holiday.data;
  for (const year in holidayList) {
    if (holidayList.hasOwnProperty(year)) {
      const yearData = holidayList[year];
      if (year == nowYear) {
        for (const day in yearData) {
          if (yearData.hasOwnProperty(day)) {
            const dayData = yearData[day];
            if (nowDate == day && dayData.holiday) {
              check = true;
            }
          }
        }
      }
    }
  }
  return check;
};

var toNum = a => {
  var a = a.toString();
  var c = a.split(".");
  var num_place = ["", "0", "00", "000", "0000"],
    r = num_place.reverse();
  for (var i = 0; i < c.length; i++) {
    var len = c[i].length;
    c[i] = r[len] + c[i];
  }
  var res = c.join("");
  console.log(res);
  return res;
};

var cpr_version = (a, b) => {
  var _a = toNum(a),
    _b = toNum(b);
  if (_a == _b) console.log("版本号相同！版本号为：" + a);
  if (_a > _b) console.log("版本号" + a + "是新版本！");
  if (_a < _b) console.log("版本号" + b + "是新版本！");
};

var isDuringDate = () => {
  var curDate = new Date();
  if (checkHoliday(curDate)) {
    return false;
  }
  var beginDateAM = new Date();
  var endDateAM = new Date();
  var beginDatePM = new Date();
  var endDatePM = new Date();

  beginDateAM.setHours(9, 30, 0);
  endDateAM.setHours(11, 35, 0);
  beginDatePM.setHours(13, 0, 0);
  endDatePM.setHours(15, 5, 0);
  if (curDate.getDay() == "6" || curDate.getDay() == "0") {
    return false;
  } else if (curDate >= beginDateAM && curDate <= endDateAM) {
    return true;
  } else if (curDate >= beginDatePM && curDate <= endDatePM) {
    return true;
  } else {
    return false;
  }
};

var setBadge = (fundcode, Realtime) => {
  let url =
    "http://fundgz.1234567.com.cn/js/" +
    fundcode +
    ".js?rt=" +
    new Date().getTime();
  axios
    .get(url)
    .then(res => {
      let val = res.data.match(/\{(.+?)\}/);
      let ress = JSON.parse(val[0]);
      chrome.browserAction.setBadgeText({
        text: ress.gszzl
      });
      let color = Realtime ?
        ress.gszzl >= 0 ?
        "#F56C6C" :
        "#4eb61b" :
        "#4285f4";
      chrome.browserAction.setBadgeBackgroundColor({
        color: color
      });
    })
    .catch(error => {
      chrome.browserAction.setBadgeText({
        text: ""
      });
    });
};

var startInterval = RealtimeFundcode => {
  chrome.browserAction.setBadgeTextColor({color: "#ffffff"});
  endInterval(Interval);
  let Realtime = isDuringDate();
  setBadge(RealtimeFundcode, Realtime);
  Interval = setInterval(() => {
    if (isDuringDate()) {
      setBadge(RealtimeFundcode, true);
    } else {
      chrome.browserAction.setBadgeBackgroundColor({
        color: "#4285f4"
      });
    }
  }, 2 * 60 * 1000);
};

var endInterval = () => {
  clearInterval(Interval);
  chrome.browserAction.setBadgeText({
    text: ""
  });
};

var runStart = RealtimeFundcode => {
  if (RealtimeFundcode) {
    startInterval(RealtimeFundcode);
  } else {
    endInterval();
  }
};

var RealtimeFundcode = null;
chrome.storage.sync.get(["holiday", "RealtimeFundcode"], res => {
  RealtimeFundcode = res.RealtimeFundcode ? res.RealtimeFundcode : null;
  if (res.holiday) {
    holiday = res.holiday;
    runStart(RealtimeFundcode);
  } else {
    getHoliday().then(res => {
      chrome.storage.sync.set({
          holiday: res.data
        },
        () => {
          holiday = res.data;
          runStart(RealtimeFundcode);
        }
      );
    });
  }
});
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type == "DuringDate") {
    let DuringDate = isDuringDate();
    sendResponse({
      farewell: DuringDate
    });
  }
  if (request.type == "endInterval") {
    endInterval();
  }
  if (request.type == "startInterval") {
    startInterval(request.id);
  }
  if (request.type == "refreshBadge") {
    chrome.browserAction.setBadgeText({
      text: request.data.gszzl
    });
    let color = isDuringDate() ?
      request.data.gszzl >= 0 ?
      "#F56C6C" :
      "#4eb61b" :
      "#4285f4";
    chrome.browserAction.setBadgeBackgroundColor({
      color: color
    });
  }
});