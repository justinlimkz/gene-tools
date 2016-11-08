#include <iostream>
#include <fstream>
#include <cstdio>
#include <string>
#include <map>
using namespace std;

map<string, string> MAP;
ifstream in;

void get_map() {
	string proteinID, gene_name;
	while (in >> proteinID >> gene_name) {
		MAP[proteinID] = gene_name;
	}
}

int main() {
	in.open("proteinID_to_gene_name.txt");
	get_map();
	string proteinID;
	int numberFound = 0;
	in.close();
	while (cin >> proteinID) {
		if (MAP[proteinID] != "") {
			cout << proteinID << " " << MAP[proteinID] << '\n';
			numberFound++;
		}
	}
	cout << "Found " << numberFound << " matches.\n";
	return 0;
}