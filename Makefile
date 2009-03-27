clean:
	find -name "*~" | xargs rm -f
	find -name "*.pyc" | xargs rm -f
	find -name "*.log" | xargs rm -f
	find -name "*.pid" | xargs rm -f


superclean: clean
	python setup.py clean
	dh_clean
	rm -rf build dist python-build-stamp-2.5
	cd webpanel && make clean
