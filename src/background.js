import axios from 'axios';


var Interval;
var isDuringDate = () => {
	var curDate = new Date();
	var beginDateAM = new Date();
	var endDateAM = new Date();
	var beginDatePM = new Date();
	var endDatePM = new Date();

	beginDateAM.setHours(9, 30, 0);
	endDateAM.setHours(11, 30, 0);
	beginDatePM.setHours(13, 0, 0);
	endDatePM.setHours(15, 0, 0);
	if (curDate.getDay() == '6' || curDate.getDay() == '0') {
		return false;
	} else if (curDate >= beginDateAM && curDate <= endDateAM) {
		return true;
	} else if (curDate >= beginDatePM && curDate <= endDatePM) {
		return true;
	} else {
		return false;
	}
}

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
			let color = Realtime ? ress.gszzl > 0 ? '#F56C6C' : '#4eb61b' : [0, 0, 0, 0];
			chrome.browserAction.setBadgeBackgroundColor({
				color: color
			});
		})
		.catch(error => {
			chrome.browserAction.setBadgeText({
				text: ''
			});
		});


}

var startInterval = RealtimeFundcode => {
	endInterval(Interval);
	let Realtime = isDuringDate();
	setBadge(RealtimeFundcode, Realtime);
	Interval = setInterval(() => {
		if (isDuringDate()) {
			setBadge(RealtimeFundcode, true);
		} else {
			chrome.browserAction.setBadgeBackgroundColor({
				color: [0, 0, 0, 0]
			});
		}
	}, 3 * 60 * 1000)

}

var endInterval = () => {
	clearInterval(Interval);
	chrome.browserAction.setBadgeText({
		text: ''
	});
}

var RealtimeFundcode = null;

chrome.storage.sync.get('RealtimeFundcode', (res) => {
	RealtimeFundcode = res.RealtimeFundcode ? res.RealtimeFundcode : null;
	if (RealtimeFundcode) {
		startInterval(RealtimeFundcode);
	} else {
		endInterval();
	}
});


chrome.runtime.onMessage.addListener(
	function (request, sender, sendResponse) {
		if (request.type == "DuringDate") {
			let DuringDate = isDuringDate();
			sendResponse({
				farewell: DuringDate
			});
		}
		if (request.type == "endInterval") {
			endInterval()
		}
		if (request.type == "startInterval") {
			startInterval(request.id)
		}
		if (request.type == "refreshBadge") {
			chrome.browserAction.setBadgeText({
				text: request.data.gszzl
			});
			let color = isDuringDate() ? request.data.gszzl > 0 ? '#F56C6C' : '#4eb61b' : [0, 0, 0, 0];
			chrome.browserAction.setBadgeBackgroundColor({
				color: color
			});
		}

	});