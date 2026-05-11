~~~cpp
#include<bits/stdc++.h>
using namespace std;

const 	int 	CNT_EM_INFO_INT  	= 4;
const 	int 	CNT_EM_INFO_CHAR 	= 5;
const 	int 	CNT_EM_LEVEL		= 5;
const 	int 	CNT_EM_WEIGHT		= 5;
const 	int 	MAX_DIGIT_ID 		= 4;
const 	int 	MAX_DIGIT_AGE 	 	= 3;
const 	int 	MAX_DIGIT_NAME 		= 8;
const 	int 	MAX_DIGIT_ADDRESS 	= 8;
const 	int 	MAX_DIGIT_CITY 		= 8;
const 	int 	MAX_DIGIT_SCORE 	= 3;
const 	int 	MAX_DIGIT_POSTCODE	= 6;
const 	char* 	BARRIER 			= " | ";

enum RE_WEIGHT 	  	{TECH_W,  			IQ_W, EQ_W,   CREDIT_W,  DILIG_W};
enum EM_LEVEL 	  	{TECH_L,  			IQ_L, EQ_L,   CREDIT_L,  DILIG_L};
enum EM_INFO_CHAR	{MAJOR ,  			NAME, CITY,   POST_CODE, ADDRESS};
enum EM_INFO_INT 	{ID=CNT_EM_LEVEL,	AGE , GENDER, SCORE};
enum COMPARE_TYPE   {SMALL_TO_BIG,		BIG_TO_SMALL};

// announcement
class Employee;
class Register;
bool emCmpSmallToBig(Employee* em1, Employee* em2);
bool emCmpBigToSmall(Employee* em1, Employee* em2);

class Employee {
private:
	int 		emLevel	  [CNT_EM_LEVEL];					// personal ability attribution
	int 		emInfoInt [CNT_EM_LEVEL+CNT_EM_INFO_INT];	// personal info: int
	const char*	emInfoChar[CNT_EM_INFO_CHAR];				// personal info: char*
public:
	Employee();
	void 		display();
	void 		setName(const char* _name);
	void 		setValue(int _info, int _value);
	void 		setValue(int _info, const char* _value);
	int			getScore();// only return
	int  		getScore(const float* _w);// calc and return
	bool		operator>(const Employee& _em);
};

class Register {
private:
	int 				reSumEmployees; // useless -> reList.size() is better and accurate
	float 				reWeight[CNT_EM_WEIGHT];    // ability weight
	vector<Employee*>	reList;// all employees
public:
	Register();
	void                add(Employee& em);
	void 				display();
	void                reSort(int _s, int _e, int _cmpType);// sort (> || <)
	void 				setW(int _w, int _value);
	int                 getSize();// get the amount of employees
	float* 				getW();
//	vector<Employee*>	select();// select out employees (top n || end n || range a b)
//	void                delt();
};

signed main() {
	srand(20250411);
	Register re;
	Employee em1;
	Employee em2;
	// set random employee level
	for (int level=0; level<CNT_EM_LEVEL; ++level) {
		em1.setValue(level, rand()%101);
		em2.setValue(level, rand()%101);
	}
	// set em1 info
	em1.setName("Queen");
	em1.setValue(ID, 		11);
	em1.setValue(AGE, 		22);
	em1.setValue(GENDER, 	0);
	em1.setValue(ADDRESS, 	"CHINA");
	em1.setValue(CITY, 		"CQ");
	em1.setValue(POST_CODE, "444888");
	em1.setValue(SCORE, 	em1.getScore(re.getW()));// is level 0 ?
	// set em2 info
	em2.setName("King");
	em2.setValue(ID, 		12);
	em2.setValue(AGE, 		28);
	em2.setValue(GENDER, 	1);
	em2.setValue(SCORE, 	em2.getScore(re.getW()));// is level 0 ?
//	em1.display();
//	em2.display();
	re.add(em1);
	re.add(em2);
	re.reSort(0, re.getSize(), BIG_TO_SMALL);
	re.display(); // used Employee.display()
	cout << endl << endl;
	re.reSort(0, re.getSize(), SMALL_TO_BIG);
	re.display();
	return 0;
}

bool emCmpSmallToBig(Employee* em1, Employee* em2) {
	return em1->getScore() < em2->getScore();
}

bool emCmpBigToSmall(Employee* em1, Employee* em2) {
	return em1->getScore() > em2->getScore();
}

void Register::reSort(int _s, int _e, int _cmpType) {
	if (reList.size() <= 1) return;
	if (_cmpType == SMALL_TO_BIG) sort(reList.begin()+_s, reList.begin()+_e, emCmpSmallToBig);
	else if (_cmpType == BIG_TO_SMALL) sort(reList.begin()+_s, reList.begin()+_e, emCmpBigToSmall);
}

void Register::add(Employee& em) {
	 reList.push_back(&em);
	 reSumEmployees = reList.size();
}

void Register::display() {
	cout << "Register Info: (Only parts of the personal detailed infos)" << endl << endl;
	int size = reList.size();
	if (size <= 0) {
		cout << "None info" << endl;
		return;
	}
	
	for (int i=0; i<size; ++i) {
		cout << "[" << i << "]" << BARRIER;
		reList[i]->display();
	}
}

void Register::setW(int _w, int _value) {
	reWeight[_w] = _value;
}

int Register::getSize() {
	return reList.size();
}

float* Register::getW() {
	return reWeight;
}

Register::Register() {
	reSumEmployees 		= 0;
	// init default weight
	reWeight[TECH_W] 	= 0.24;
	reWeight[IQ_W] 		= 0.27;
	reWeight[EQ_W] 		= 0.20;
	reWeight[CREDIT_W] 	= 0.13;
	reWeight[DILIG_W] 	= 0.16;
}





int  Employee::getScore() {
	return emInfoInt[SCORE];
}

void Employee::setName(const char* _name) {
	emInfoChar[NAME] = _name;
}

void Employee::setValue(int _info, int _value) {
	if (_info >= CNT_EM_LEVEL) {
		emInfoInt[_info] = _value;
	}
	else emLevel[_info] = _value;	
}

void Employee::setValue(int _info, const char* _value) {
	emInfoChar[_info] = _value;
}

void Employee::display() {	

	cout << "ID: "   	 << setw(MAX_DIGIT_ID)  	 << setfill('0')  <<right 	<< emInfoInt[ID]    << BARRIER
		 << "Name: " 	 << setw(MAX_DIGIT_NAME) 	 << setfill(' ')   <<left 	<< emInfoChar[NAME] << BARRIER
	 	 << "Age: "  	 << setw(MAX_DIGIT_AGE)  	 << emInfoInt[AGE]      	<< BARRIER
		 << "Address: "  << setw(MAX_DIGIT_ADDRESS)  << emInfoChar[ADDRESS] 	<< BARRIER
		 << "City: "  	 << setw(MAX_DIGIT_CITY)  	 << emInfoChar[CITY]    	<< BARRIER
		 << "Score: " 	 << setw(MAX_DIGIT_SCORE)    << emInfoInt[SCORE]  		<< BARRIER
		 << "PostCode: " << setw(MAX_DIGIT_POSTCODE) << emInfoChar[POST_CODE] 	<< BARRIER
		 << endl;
}

int  Employee::getScore(const float* _w) {
	float score = 0;
	for (int cnt=0; cnt < CNT_EM_LEVEL; ++cnt) {
		score += _w[cnt] * emLevel[cnt];
	}
	return floor(score);
}

bool Employee::operator>(const Employee& _em) {
	return this->emInfoInt[SCORE] > _em.emInfoInt[SCORE] ? true : false;
}

Employee::Employee() {
	for (int i=0; i<CNT_EM_INFO_CHAR; ++i) {
		emInfoChar[i]="None";
	}

	for (int i=0; i<CNT_EM_INFO_INT; ++i) {
		emInfoInt[i+CNT_EM_LEVEL]=0;
	}
	
	for (int i=0; i<CNT_EM_LEVEL; ++i) {
		emLevel[i]=0;
	}
} 
~~~

