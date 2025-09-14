Contributing
============

We welcome contributions to `py-amr2fred` and encourage developers of all skill levels to contribute! To help us maintain the quality and consistency of the project, please follow the guidelines below:

1. **Fork the repository**
   Start by forking the repository to your GitHub account. You can do this by clicking the "Fork" button at the top-right of the repository page.

2. **Clone your fork**
   Clone your fork to your local machine using the following command:

.. code-block:: bash

    git clone https://github.com/infovillasimius/py-amr2fred.git


3. **Create a feature branch**
Before making any changes, create a new branch to work on your feature or bug fix. This keeps the `main` branch clean and allows for easy collaboration:

.. code-block:: bash

    git checkout -b feature-new

4. **Make your changes**
Now you can begin making your changes! Ensure that your code follows the project’s coding standards and that any new features are well-tested. If you’re fixing a bug, make sure to include a test case that demonstrates the issue and how your changes resolve it.

5. **Commit your changes**
Once you've made your changes, commit them with a meaningful commit message. For example:

.. code-block:: bash

    git commit -m "Fix bug in AMR-to-RDF conversion"

6. **Push your changes**
Push your changes to your forked repository:

.. code-block:: bash

    git push origin feature-new

7. **Submit a Pull Request**
Go to the GitHub page of your fork and click "New Pull Request." Make sure the base repository is infovillasimius/py_amr2fred and select development as the branch to merge into. Provide a description of your changes and any relevant details, then submit the pull request.


Coding Standards
----------------
To ensure that the codebase remains clean and easy to maintain, please follow these coding standards:

- **PEP 8 guidelines**
  Ensure your code adheres to the PEP 8 guidelines for Python code style. This includes proper indentation, line length, naming conventions, and spacing around operators. You can use tools like `flake8 <https://flake8.pycqa.org/>`_ to check the code style.

- **Docstrings**
  Include docstrings for all functions, classes, and methods. This helps others understand the purpose of your code and how to use it. Use the following format for function docstrings:

  .. code-block:: python

      def example_function(param1, param2):
          """
          Brief description of the function.

          Parameters:
              param1 (type): Description of param1
              param2 (type): Description of param2

          Returns:
              type: Description of the return value
          """
          # function code

- **Testing**
  If you're adding new features or fixing bugs, write unit tests to cover your changes. Make sure the tests are clear, concise, and test the expected behavior.

- **Avoid unnecessary changes**
  Do not make changes to unrelated parts of the codebase (such as formatting or refactoring unrelated code) in the same pull request.

By following these steps and guidelines, you’ll be able to contribute to the project efficiently and help maintain a high-quality codebase. Thank you for contributing!
