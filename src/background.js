import axios from "axios";

var Interval;
var holiday;
var RealtimeFundcode = null;
var fundListM = [];
var showBadge = 1;
var BadgeContent = 1;
var BadgeType = 1;
var userId = null;

var getGuid = () => {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (
    c
  ) {
    var r = (Math.random() * 16) | 0,
      v = c == "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}
var getHoliday = () => {
  let url = "https://rabt.gitee.io/funds/holiday.json";
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

  //时区转换为东8区
  var zoneOffset = 8;
  var offset8 = new Date().getTimezoneOffset() * 60 * 1000;
  var nowDate8 = new Date().getTime();
  var curDate = new Date(nowDate8 + offset8 + zoneOffset * 60 * 60 * 1000);

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

var formatNum = val => {
  let num = parseFloat(val);
  let absNum = Math.abs(num);
  if (absNum < 10) {
    return num.toFixed(2);
  } else if (absNum < 100) {
    return num.toFixed(1);
  } else if (absNum < 1000) {
    return num.toFixed(0);
  } else if (absNum < 10000) {
    return (num / 1000).toFixed(1) + 'k';
  } else if (absNum < 1000000) {
    return (num / 1000).toFixed(0) + 'k';
  } else if (absNum < 10000000) {
    return (num / 1000000).toFixed(1) + 'M';
  } else {
    return (num / 1000000).toFixed(0) + 'M';
  }
}

var setBadge = (fundcode, Realtime, type) => {
  let fundStr = null;
  if (type == 1) {
    fundStr = fundcode;
  } else {
    fundStr = fundListM.map((val) => val.code).join(",");
  }

  let url =
    "https://fundmobapi.eastmoney.com/FundMNewApi/FundMNFInfo?pageIndex=1&pageSize=50&plat=Android&appType=ttjj&product=EFund&Version=1&deviceid=" + userId + "&Fcodes=" +
    fundStr;
  axios
    .get(url)
    .then((res) => {
      let allAmount = 0;
      let allGains = 0;
      let textStr = null;
      if (type == 1) {
        let val = res.data.Datas[0];
        let data = {
          fundcode: val.FCODE,
          name: val.SHORTNAME,
          jzrq: val.PDATE,
          dwjz: val.NAV,
          gsz: isNaN(val.GSZ) ? null : val.GSZ,
          gszzl: isNaN(val.GSZZL) ? 0 : val.GSZZL,
          gztime: val.GZTIME,
          num: 0
        };
        let slt = fundListM.filter(
          (item) => item.code == data.fundcode
        );
        if (!slt.length) {
          return false;
        }
        data.num = slt[0].num;
        var sum = 0;

        let num = data.num ? data.num : 0;

        if (val.PDATE == val.GZTIME.substr(0, 10)) {
          data.gsz = val.NAV;
          data.gszzl = isNaN(val.NAVCHGRT) ? 0 : val.NAVCHGRT;
          sum = (
            (data.dwjz - data.dwjz / (1 + data.gszzl * 0.01)) *
            num
          ).toFixed(1);
        } else {
          if (data.gsz) {
            sum = ((data.gsz - data.dwjz) * num).toFixed(1);
          }

        }


        if (BadgeType == 1) {
          textStr = data.gszzl;
        } else {
          if (num != 0) {
            textStr = formatNum(sum);
          } else {
            textStr = "0";
          }
        }

      } else {
        res.data.Datas.forEach((val) => {
          let slt = fundListM.filter(
            (item) => item.code == val.FCODE
          );
          let num = slt[0].num ? slt[0].num : 0;
          allAmount += val.NAV * num;
          var sum = 0;
          if (val.PDATE == val.GZTIME.substr(0, 10)) {
            sum = (val.NAV - val.NAV / (1 + val.NAVCHGRT * 0.01)) * num
          } else {
            let gsz = isNaN(val.GSZ) ? null : val.GSZ
            if (gsz) {
              sum = (gsz - val.NAV) * num
            }
          }
          allGains += sum;

        });
        if (BadgeType == 1) {
          if (allAmount == 0 || allGains == 0) {
            textStr = "0"
          } else {
            textStr = (100 * allGains / allAmount).toFixed(2);
          }

        } else {
          textStr = formatNum(allGains);
        }
      }


      chrome.browserAction.setBadgeText({
        text: textStr
      });
      let color = Realtime ?
        allGains >= 0 ?
        "#F56C6C" :
        "#4eb61b" :
        "#4285f4";
      chrome.browserAction.setBadgeBackgroundColor({
        color: color
      });

    })
    .catch((error) => {

    });


};


var startInterval = (RealtimeFundcode, type = 1) => {
  endInterval(Interval);
  let Realtime = isDuringDate();
  RealtimeFundcode = RealtimeFundcode;
  setBadge(RealtimeFundcode, Realtime, type);
  Interval = setInterval(() => {
    if (isDuringDate()) {
      setBadge(RealtimeFundcode, true, type);
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

  if (showBadge == 1 && BadgeContent == 1) {
    if (RealtimeFundcode) {
      startInterval(RealtimeFundcode);
    } else {
      endInterval();
    }
  } else if (showBadge == 1 && BadgeContent == 2) {
    startInterval(null, 2);
  } else {
    endInterval();
  }

};


var getData = () => {
  chrome.storage.sync.get(["holiday", "fundListM", "RealtimeFundcode", "showBadge", "BadgeContent", "BadgeType", "userId"], res => {
    RealtimeFundcode = res.RealtimeFundcode ? res.RealtimeFundcode : null;
    fundListM = res.fundListM ? res.fundListM : [];
    showBadge = res.showBadge ? res.showBadge : 1;
    BadgeContent = res.BadgeContent ? res.BadgeContent : 1;
    BadgeType = res.BadgeType ? res.BadgeType : 1;
    if (res.userId) {
      userId = res.userId;
    } else {
      userId = getGuid();
      chrome.storage.sync.set({
        userId: userId,
      });
    }
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
}

getData();


chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type == "DuringDate") {
    let DuringDate = isDuringDate();
    sendResponse({
      farewell: DuringDate
    });
  }
  if (request.type == "refresh") {
    getData();
  }
  if (request.type == "refreshBadgeAllGains") {
    let allAmount = 0;
    let allGains = 0;
    request.data.forEach((val) => {
      let slt = fundListM.filter(
        (item) => item.code == val.FCODE
      );
      let num = slt[0].num ? slt[0].num : 0;
      allAmount += val.NAV * num;
      var sum = 0;
      if (val.PDATE == val.GZTIME.substr(0, 10)) {
        sum = (val.NAV - val.NAV / (1 + val.NAVCHGRT * 0.01)) * num
      } else {
        let gsz = isNaN(val.GSZ) ? null : val.GSZ;
        if (gsz) {
          sum = (gsz - val.NAV) * num;
        }

      }
      allGains += sum;

    });
    let textStr = null;
    if (BadgeType == 1) {
      if (allAmount == 0 || allGains == 0) {
        textStr = "0"
      } else {
        textStr = (100 * allGains / allAmount).toFixed(2);
      }

    } else {
      textStr = formatNum(allGains);
    }

    chrome.browserAction.setBadgeText({
      text: textStr
    });
    let color = isDuringDate() ?
      allGains >= 0 ?
      "#F56C6C" :
      "#4eb61b" :
      "#4285f4";
    chrome.browserAction.setBadgeBackgroundColor({
      color: color
    });
  }
  if (request.type == "endInterval") {
    endInterval();
  }
  if (request.type == "startInterval") {
    startInterval(request.id);
  }
  if (request.type == "refreshOption") {
    switch (request.data.type) {
      case "showBadge":
        showBadge = request.data.value;
        break;
      case "BadgeContent":
        BadgeContent = request.data.value;
        break;
      case "BadgeType":
        BadgeType = request.data.value;
        break;
    }
    getData();
  }
  if (request.type == "refreshBadge") {
    let textstr = null;
    if (BadgeType == 1) {
      textstr = request.data.gszzl;
    } else {

      textstr = formatNum(val.gains);
    }
    chrome.browserAction.setBadgeText({
      text: textstr
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