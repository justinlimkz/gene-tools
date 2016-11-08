#include <iostream>
#include <fstream>
#include <cstdio>
#include <string>
using namespace std;

int main() {
	freopen ("HUMAN_9606_idmapping.txt", "r", stdin);
	freopen ("proteinID_to_gene_name.txt", "w", stdout);
	string proteinID, attribute, value;
	while (cin >> proteinID >> attribute >> value) {
		if (attribute == "Gene_Name") {
			cout << proteinID << " " << value << '\n';
		}
	}
	return 0;
}